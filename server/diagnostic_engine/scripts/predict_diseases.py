import subprocess
import sqlite3
import pandas as pd
from pathlib import Path
from typing import Literal

def predict_diseases(
    gene: Literal["BRCA1", "TP53", "PTEN"],
    patient_fasta: str,
    output_csv_path: str
):
    """
    Predict diseases for a given gene based on patient's FASTA file.

    Args:
        gene (str): Gene name (BRCA1, TP53, PTEN)
        patient_fasta (str): Path to patient's FASTA file
        output_csv_path (str): Path to save the matched disease predictions
    """
    # Static configuration
    OFFSETS = {
        "BRCA1": 43044294,
        "TP53":  7661778,
        "PTEN":  87863224,
    }

    REFS = {
        "BRCA1": "../data/references/brca1_reference.fasta",
        "TP53":  "../data/references/tp53_reference.fasta",
        "PTEN":  "../data/references/pten_reference.fasta",
    }

    DB_PATH = "../data/clinvar/clinvar.db"

    if gene not in OFFSETS or gene not in REFS:
        raise ValueError("Invalid gene. Supported genes: BRCA1, TP53, PTEN")

    genomic_offset = OFFSETS[gene]
    reference_fasta = REFS[gene]
    blast_output = Path(output_csv_path).with_suffix(".blast.tsv")

    # Ensure output directory exists
    Path(output_csv_path).parent.mkdir(parents=True, exist_ok=True)

    print("🔬 Running BLAST...")
    subprocess.run([
        "makeblastdb", "-in", reference_fasta, "-dbtype", "nucl", "-out", "temp_db"
    ], check=True)

    subprocess.run([
        "blastn", "-query", patient_fasta, "-db", "temp_db",
        "-outfmt", "6 qseqid sseqid pident length mismatch gapopen qstart qend sstart send evalue bitscore qseq sseq",
        "-out", str(blast_output)
    ], check=True)

    print("✅ BLAST completed. Extracting mutations...")
    cols = [
        "qseqid", "sseqid", "pident", "length", "mismatch", "gapopen",
        "qstart", "qend", "sstart", "send", "evalue", "bitscore",
        "qseq", "sseq"
    ]
    df = pd.read_csv(blast_output, sep='\t', names=cols)
    mutations = []

    for _, row in df.iterrows():
        qseq, sseq = row["qseq"], row["sseq"]
        sstart, send = int(row["sstart"]), int(row["send"])

        ref_pos = min(sstart, send)
        direction = 1 if send >= sstart else -1

        pos = ref_pos
        for q_base, s_base in zip(qseq, sseq):
            if q_base != '-' and s_base != '-':
                if q_base.upper() != s_base.upper():
                    genomic_pos = pos + genomic_offset
                    mutations.append({
                        "position": genomic_pos,
                        "ref_base": s_base.upper(),
                        "alt_base": q_base.upper()
                    })
                pos += direction
            elif q_base == '-' and s_base != '-':
                pos += direction  # skip deletion
            elif s_base == '-' and q_base != '-':
                pass  # skip insertion

    if not mutations:
        print("⚠️ No mutations found in patient sample.")
        return

    mutations_df = pd.DataFrame(mutations)

    print("🧾 Comparing with ClinVar database...")
    table_name = f"{gene.lower()}_variants"
    conn = sqlite3.connect(DB_PATH)
    query = f"""
    SELECT Start AS position, ReferenceAllele AS ref_base, AlternateAllele AS alt_base,
           ClinicalSignificance AS clinical_significance, PhenotypeList AS disease
    FROM {table_name}
    WHERE ClinicalSignificance LIKE '%Pathogenic%' AND Type = 'single nucleotide variant'
    """
    clinvar_df = pd.read_sql_query(query, conn)
    conn.close()

    clinvar_df["ref_base"] = clinvar_df["ref_base"].str.upper()
    clinvar_df["alt_base"] = clinvar_df["alt_base"].str.upper()

    matched = pd.merge(
        mutations_df,
        clinvar_df,
        how="inner",
        on=["position", "ref_base", "alt_base"]
    )

    matched.to_csv(output_csv_path, index=False)
    print(f"✅ Matched {len(matched)} pathogenic mutation(s). Results saved to {output_csv_path}")

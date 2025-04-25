import argparse
import subprocess
import sqlite3
import pandas as pd

from pathlib import Path

def run_blast(patient_fasta, reference_fasta, blast_output_path):
    print("🔬 Running BLAST...")
    subprocess.run([
        "makeblastdb", "-in", reference_fasta, "-dbtype", "nucl", "-out", "temp_db"
    ], check=True)
    subprocess.run([
    "blastn", "-query", patient_fasta, "-db", "temp_db",
    "-outfmt", "6 qseqid sseqid pident length mismatch gapopen qstart qend sstart send evalue bitscore qseq sseq",
    "-out", blast_output_path
    ], check=True)

    print("✅ BLAST completed.")


def find_mutations(blast_tsv_path, genomic_offset):
    print("🧬 Finding mutations from BLAST output...")
    cols = [
        "qseqid", "sseqid", "pident", "length", "mismatch", "gapopen",
        "qstart", "qend", "sstart", "send", "evalue", "bitscore",
        "qseq", "sseq"
    ]
    df = pd.read_csv(blast_tsv_path, sep='\t', names=cols)

    mutations = []

    for _, row in df.iterrows():
        qseq = row["qseq"]
        sseq = row["sseq"]
        sstart = int(row["sstart"])
        send = int(row["send"])

        ref_pos = sstart if sstart < send else send  # lower bound
        direction = 1 if send >= sstart else -1      # forward or reverse strand

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

    return pd.DataFrame(mutations)



def compare_with_clinvar(mutations_df, gene_name):
    print("🧾 Comparing with ClinVar database...")
    table_name = f"{gene_name.lower()}_variants"
    conn = sqlite3.connect("../data/clinvar/clinvar.db")
    query = f"""
    SELECT Start AS position, ReferenceAllele AS ref_base, AlternateAllele AS alt_base,
           ClinicalSignificance AS clinical_significance, PhenotypeList AS disease
    FROM {table_name}
    WHERE ClinicalSignificance LIKE '%Pathogenic%'
      AND Type = 'single nucleotide variant'
    """
    clinvar_df = pd.read_sql_query(query, conn)
    conn.close()

    merged = pd.merge(mutations_df, clinvar_df,
                      on=["position", "ref_base", "alt_base"],
                      how="inner")
    print(f"🧠 Matched {len(merged)} pathogenic mutations.")
    return merged


def main(args):
    Path(args.output_dir).mkdir(parents=True, exist_ok=True)

    blast_output = Path(args.output_dir) / f"blast_output_{args.gene.lower()}.tsv"
    output_file = Path(args.output_dir) / f"final_predicted_diseases_{args.gene.lower()}.csv"

    run_blast(args.patient_fasta, args.reference_fasta, str(blast_output))

    mutations_df = find_mutations(
        blast_tsv_path=str(blast_output),
        genomic_offset=args.genomic_offset
    )

    if mutations_df.empty:
        print("⚠️ No mutations found in patient sample.")
        return

    matched_diseases = compare_with_clinvar(mutations_df, args.gene)
    matched_diseases.to_csv(output_file, index=False)
    print(f"✅ Saved predicted diseases to {output_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Predict diseases based on patient FASTA sample.")
    parser.add_argument("--gene", required=True, help="Gene name (e.g. BRCA1, TP53, PTEN)")
    parser.add_argument("--genomic-offset", type=int, required=True, help="Genomic start offset of the gene")
    parser.add_argument("--patient-fasta", required=True, help="Path to patient FASTA file")
    parser.add_argument("--reference-fasta", required=True, help="Path to gene reference FASTA file")
    parser.add_argument("--output-dir", default="../data/results", help="Output directory for results")
    args = parser.parse_args()

    main(args)

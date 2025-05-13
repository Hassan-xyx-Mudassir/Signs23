import os
import streamlit as st
import pandas as pd
import tempfile
from pathlib import Path
from predict_diseases import predict_diseases

# Set up the Streamlit page configuration
st.set_page_config(page_title="Disease Predictor", layout="centered")

st.title("🧬 Disease Predictor from Patient DNA")
st.write("Upload a patient's FASTA file and select a gene to predict possible diseases.")

# Gene selection
gene = st.selectbox("Select Gene", ["BRCA1", "TP53", "PTEN"])

# File upload
uploaded_file = st.file_uploader("Upload Patient FASTA File", type=["fasta", "fa"])

# Predict button
if st.button("🔍 Predict Diseases"):
    if not uploaded_file:
        st.warning("⚠️ Please upload a FASTA file first.")
    else:
        # Save the uploaded FASTA file to a temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix=".fasta") as temp_fasta:
            temp_fasta.write(uploaded_file.read())
            temp_fasta_path = temp_fasta.name

        # Define the output directory relative to the current file
        output_dir = Path(__file__).resolve().parent.parent / "data" / "results"
        output_dir.mkdir(parents=True, exist_ok=True)

        # Define the output file path
        output_csv_path = output_dir / f"predicted_diseases_{gene.lower()}.csv"

        try:
            # Run the disease prediction function
            predict_diseases(
                gene=gene,
                patient_fasta=temp_fasta_path,
                output_csv_path=str(output_csv_path)
            )

            # Load and display the results
            if output_csv_path.exists():
                df = pd.read_csv(output_csv_path)  # Reads CSV with default comma separator
                if not df.empty:
                    st.success(f"✅ Found {len(df)} pathogenic mutation(s).")
                    # Display only the 'disease' column
                    st.dataframe(df[["disease"]])
                else:
                    st.info("ℹ️ No matching pathogenic variants found.")
            else:
                st.error("❌ Output file not created.")
        except Exception as e:
            st.error(f"An error occurred: {e}")

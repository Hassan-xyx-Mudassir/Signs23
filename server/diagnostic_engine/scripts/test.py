from predict_diseases import predict_diseases

predict_diseases(
    gene="TP53",
    patient_fasta="../data/samples/patient_tp53.fasta",
    output_csv_path="../data/results/final_predicted_diseases_tp53.csv"
)

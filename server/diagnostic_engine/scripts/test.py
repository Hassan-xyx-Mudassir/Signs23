from predict_diseases import predict_diseases


'''
All you have to do now is call the function. Pass the gene [BRCA1 | TP53 | PTEN], the path 
to the patient fasta file, and the path for the output CSV file. Then you can read the output 
file's last column to get the disease. 
'''

predict_diseases(
    gene="PTEN",
    patient_fasta="../data/samples/patient_pten.fasta",
    output_csv_path="../data/results/final_predicted_diseases_pten.csv"
)

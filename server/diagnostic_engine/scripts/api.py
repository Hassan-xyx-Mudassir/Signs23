from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import shutil
import tempfile
import pandas as pd
from predict_diseases import predict_diseases

app = FastAPI(
    title="Disease Predictor API",
    description="Predicts diseases based on DNA FASTA file and gene.",
    version="1.0"
)

# Enable CORS if needed
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Set your frontend origin(s)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/predict/")
async def predict_disease(
    gene: str = Form(..., description="Gene name (e.g., BRCA1, TP53, PTEN)"),
    fasta_file: UploadFile = File(..., description="Patient DNA FASTA file")
):
    if gene not in ["BRCA1", "TP53", "PTEN"]:
        raise HTTPException(status_code=400, detail="Unsupported gene selected.")

    try:
        # Save uploaded file to a temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix=".fasta") as temp_file:
            shutil.copyfileobj(fasta_file.file, temp_file)
            temp_fasta_path = temp_file.name

        # Output path
        output_dir = Path("data/results")
        output_dir.mkdir(parents=True, exist_ok=True)
        output_csv_path = output_dir / f"predicted_diseases_{gene.lower()}.csv"

        # Call the prediction function
        predict_diseases(
            gene=gene,
            patient_fasta=temp_fasta_path,
            output_csv_path=str(output_csv_path)
        )

        # Load results
        if output_csv_path.exists():
            df = pd.read_csv(output_csv_path)
            if not df.empty:
                return JSONResponse(
                    status_code=200,
                    content={"predicted_diseases": df["disease"].dropna().tolist()}
                )
            else:
                return JSONResponse(
                    status_code=200,
                    content={"message": "No matching pathogenic variants found."}
                )
        else:
            raise HTTPException(status_code=500, detail="Prediction output not created.")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

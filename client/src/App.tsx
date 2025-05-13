"use client";

import type React from "react";
import { useState } from "react";
import "bootstrap/dist/css/bootstrap.min.css";
import { Dna, Upload, X } from "lucide-react";

export default function DiseasePredictorPage() {
  const [selectedGene, setSelectedGene] = useState<string>("PTEN");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [fileName, setFileName] = useState<string>("");
  const [fileSize, setFileSize] = useState<string>("");
  const [isDragging, setIsDragging] = useState<boolean>(false);
  const [error, setError] = useState<string>("");
  const [isProcessing, setIsProcessing] = useState<boolean>(false);
  const [result, setResult] = useState<string[] | string | null>(null);

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);

    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const file = e.dataTransfer.files[0];
      handleFileSelection(file);
    }
  };

  const handleFileSelection = (file: File) => {
    if (!file.name.endsWith(".fasta") && !file.name.endsWith(".fa")) {
      setError("Please upload a FASTA or FA file");
      return;
    }

    if (file.size > 200 * 1024 * 1024) {
      setError("File size exceeds 200MB limit");
      return;
    }

    setSelectedFile(file);
    setFileName(file.name);
    setFileSize(`${(file.size / (1024 * 1024)).toFixed(2)}MB`);
    setError("");
  };

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      handleFileSelection(e.target.files[0]);
    }
  };

  const removeFile = () => {
    setSelectedFile(null);
    setFileName("");
    setFileSize("");
    setResult(null);
  };

  const predictDiseases = async () => {
    if (!selectedGene) {
      setError("Please select a gene");
      return;
    }

    if (!selectedFile) {
      setError("Please upload a FASTA file");
      return;
    }

    setIsProcessing(true);
    setError("");
    setResult(null);

    const formData = new FormData();
    formData.append("gene", selectedGene);
    formData.append("fasta_file", selectedFile);

    try {
      const response = await fetch("http://localhost:8000/predict/", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (response.ok) {
        if (data.predicted_diseases) {
          setResult(data.predicted_diseases);
        } else if (data.message) {
          setResult(data.message);
        }
      } else {
        setError(data.detail || "An error occurred during prediction");
      }
    } catch (err: any) {
      setError("Failed to connect to the prediction API");
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div
      className="min-vh-100 d-flex align-items-center justify-content-center"
      style={{
        background: "linear-gradient(to bottom right, #1e293b, #0f172a)",
      }}
    >
      <div className="container">
        <div className="row justify-content-center">
          <div className="col-md-8 col-lg-6">
            <div className="mb-4 d-flex justify-center align-items-center">
              <img
                src="/signs23.svg"
                alt="Logo"
                style={{
                  width: "100px",
                  height: "100px",
                  marginRight: "10px",
                  borderRadius: "50%",
                  objectFit: "cover",
                  objectPosition: "top",
                }}
              />
              <h1 className="text-white mb-0">Signs23</h1>
            </div>

            <div className="mb-4 d-flex align-items-center">
              <Dna className="me-2" size={32} color="#fb923c" />
              <h1 className="text-white mb-0">
                Disease Predictor from Patient DNA
              </h1>
            </div>

            <p className="text-light mb-4">
              Upload a patient&apos;s FASTA file and select a gene to predict
              possible diseases.
            </p>

            <div className="mb-4">
              <label htmlFor="gene-select" className="form-label text-light">
                Select Gene
              </label>
              <select
                className="form-select bg-secondary text-white"
                id="gene-select"
                value={selectedGene}
                onChange={(e) => setSelectedGene(e.target.value)}
              >
                <option value="PTEN">PTEN</option>
                <option value="BRCA1">BRCA1</option>
                <option value="TP53">TP53</option>
              </select>
            </div>

            <div className="mb-4">
              <label className="form-label text-light">
                Upload Patient FASTA File
              </label>
              <div
                className={`border border-2 border-dashed rounded p-4 text-center ${
                  isDragging
                    ? "border-primary bg-dark bg-opacity-75"
                    : "border-secondary bg-dark bg-opacity-50"
                }`}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                style={{ minHeight: "150px" }}
              >
                <div className="d-flex flex-column align-items-center justify-content-center">
                  <Upload className="mb-2" size={40} color="#adb5bd" />
                  <p className="text-light mb-1">Drag and drop file here</p>
                  <p className="text-muted small">
                    Limit 200MB per file • FASTA/FA
                  </p>
                  <input
                    id="file-upload"
                    type="file"
                    accept=".fasta,.fa"
                    className="d-none"
                    onChange={handleFileInputChange}
                  />
                  <button
                    className="btn btn-outline-secondary mt-2"
                    onClick={() =>
                      document.getElementById("file-upload")?.click()
                    }
                  >
                    Browse files
                  </button>
                </div>
              </div>
            </div>

            {fileName && (
              <div className="mb-4 d-flex align-items-center p-2 bg-dark bg-opacity-50 rounded border border-secondary">
                <div className="p-2 bg-secondary rounded me-2">
                  <Upload size={20} color="#e9ecef" />
                </div>
                <div className="flex-grow-1 text-truncate">
                  <p className="text-light mb-0 small">{fileName}</p>
                  <p className="text-muted mb-0 small">{fileSize}</p>
                </div>
                <button
                  className="btn btn-sm btn-link text-light"
                  onClick={removeFile}
                >
                  <X size={16} />
                </button>
              </div>
            )}

            <button
              className="btn btn-danger"
              onClick={predictDiseases}
              disabled={isProcessing}
              style={{ backgroundColor: "#ea580c", borderColor: "#ea580c" }}
            >
              <Dna className="me-2" size={16} />
              {isProcessing ? "Predicting..." : "Predict Diseases"}
            </button>

            {error && (
              <div
                className="alert alert-danger mt-4"
                style={{
                  backgroundColor: "rgba(127, 29, 29, 0.6)",
                  borderColor: "#991b1b",
                  color: "white",
                }}
              >
                {error}
              </div>
            )}

            {result && (
              <div className="alert alert-success mt-4">
                {Array.isArray(result) ? (
                  <>
                    <h5 className="mb-2">Predicted Diseases:</h5>
                    <ul className="mb-0">
                      {result.map((disease, idx) => (
                        <li key={idx}>{disease}</li>
                      ))}
                    </ul>
                  </>
                ) : (
                  <p>{result}</p>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

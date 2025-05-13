const BASE_URL = "http://localhost:8000"; // Backend API URL

// Function to make a POST request to the '/predict/' endpoint
export const predictDisease = async (gene, fastaFile) => {
  try {
    // Create a FormData object to handle file and other form data
    const formData = new FormData();
    formData.append("gene", gene); // append the gene
    formData.append("fasta_file", fastaFile); // append the file

    // Make the POST request with FormData
    const response = await fetch(${BASE_URL}/predict/, {
      method: "POST",
      body: formData, // Pass the FormData object in the body
    });

    if (!response.ok) {
      throw new Error("Network response was not ok");
    }

    const result = await response.json();
    return result; // return the response data from the API
  } catch (error) {
    console.error("Error:", error);
    throw error; // throw the error to handle it in the calling function
  }
};
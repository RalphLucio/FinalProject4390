"use client";
import React, { useState } from "react";
import HomeButton from "../components/HomeButton";
import Footer from "../components/Footer";

const SkinCancerPage = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);
  const [resultData, setResultData] = useState(null); // State to store the results

  const handleFileChange = (event) => {
    setSelectedFile(event.target.files[0]);
    setIsSuccess(false); // Reset success state when a new file is selected
    setResultData(null); // Reset results when a new file is selected
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!selectedFile) {
      alert("Please select a file first!");
      return;
    }

    setIsLoading(true);
    try {
      const formData = new FormData();
      formData.append("file", selectedFile);
      console.log(formData);

      const response = await fetch("https://8sd395mr-5000.usw3.devtunnels.ms/upload", {
        method: "POST",
        body: formData,
      });

      // Ensure the response is ok and parse it
      if (!response.ok) {
        throw new Error("Failed to upload file");
      }

      const result = await response.json(); // Parse the JSON response
      console.log("Response Data", result);

      // Set the result data and mark success
      setResultData(result);
      setIsSuccess(true); // Set success state
    } catch (error) {
      console.error("File upload failed:", error);
      setIsSuccess(false); // Mark success as false on error
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-background-100">
      <div className="flex items-center justify-center m-2">
        <h1 className="text-text-950 text-4xl">
          Medi<span className="font-bold text-accent-500">Scan</span>
        </h1>
      </div>
      <div className="flex flex-1 items-center justify-center w-full">
        <div className="bg-coal p-8 rounded-lg shadow-lg w-full max-w-md">
          <h1 className="text-3xl font-bold mb-4 text-blue-600 text-center">
            Upload Skin Picture
          </h1>
          <p className="mb-4 text-white">
            Please upload a clear picture of your skin. Our skin cancer
            detection model will analyze the image to provide you with a
            preliminary assessment. Ensure the image is well-lit and focused for
            the best results.
          </p>
          {isSuccess && (
            <div
              className="alert alert-success text-center mb-4 text-white"
              role="alert"
            >
              File uploaded successfully!
            </div>
          )}
          <form onSubmit={handleSubmit} className="space-y-4">
            <input
              type="file"
              accept="image/*"
              onChange={handleFileChange}
              className="block w-full text-sm text-gray-900 border border-gray-300 rounded-lg cursor-pointer bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
            {isLoading ? (
              <div className="flex justify-center">
                <div className="loader ease-linear rounded-full border-4 border-t-4 border-gray-200 h-12 w-12"></div>
              </div>
            ) : (
              <button
                type="submit"
                className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition duration-300 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50"
              >
                Submit
              </button>
            )}
          </form>

          {/* Display results if available */}
          {resultData && (
            <div className="mt-6 p-4 shadow-md">
              <h2 className="text-xl font-bold text-white">Results</h2>
              <p className="text-white"><strong>Name:</strong> {resultData.name}</p>
              <p className="text-white"><strong>Cancer Prediction:</strong> {resultData.cancer_pred}</p>
              <p className="text-white"><strong>Hash:</strong> {resultData.hash}</p>
              <p className="text-white"><strong>URL:</strong> <img src={resultData.url} alt="" /></p>
              <button
                onClick={() => setResultData(null)} // Reset the results
                className="mt-4 bg-red-600 py-2 px-4 rounded-lg hover:bg-red-700"
              >
                Upload Another Image
              </button>
            </div>
          )}
        </div>
      </div>
      <div className="mt-auto mb-9">
        <Footer />
      </div>
      <div className="absolute bottom-9 right-12">
        <HomeButton />
      </div>
    </div>
  );
};

export default SkinCancerPage;


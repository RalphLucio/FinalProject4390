"use client";
import React, { useState } from "react";
import HomeButton from "../components/HomeButton";
import Footer from "../components/Footer";

const SkinCancerPage = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);

  const handleFileChange = (event) => {
    setSelectedFile(event.target.files[0]);
    setIsSuccess(false); // Reset success state when a new file is selected
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!selectedFile) {
      alert("Please select a file first!");
      return;
    }

    setIsLoading(true);

    try {
      // Simulate file upload
      await new Promise((resolve) => setTimeout(resolve, 1000));

      // Here you would typically handle the file submission to the backend
      // For example, using fetch or axios to send a POST request
      console.log("File submitted:", selectedFile);
      setIsSuccess(true); // Set success state
    } catch (error) {
      console.error("File upload failed:", error);
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

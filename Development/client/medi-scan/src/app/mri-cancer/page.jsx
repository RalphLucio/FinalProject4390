"use client";
import React, { useState } from "react";
import HomeButton from "../components/HomeButton";
import Footer from "../components/Footer";

const MriCancerPage = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [segmentedImage, setSegmentedImage] = useState("");
  const [errorMessage, setErrorMessage] = useState("");

  const handleFileChange = (event) => {
    setSelectedFile(event.target.files[0]);
    setSegmentedImage(""); // Reset segmented image when a new file is selected
    setErrorMessage(""); // Clear previous error messages
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!selectedFile) {
      alert("Please select a file first!");
      return;
    }

    setIsLoading(true);

    const reader = new FileReader();
    reader.onload = async (e) => {
      const base64Image = e.target.result.split(",")[1];
      const payload = { image: base64Image };

      try {
        const response = await fetch("http://127.0.0.1:5000/predict", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(payload),
        });

        if (!response.ok) {
          throw new Error(`Error: ${response.status} - ${response.statusText}`);
        }

        const data = await response.json();

        // Display segmented image
        setSegmentedImage(`data:image/jpeg;base64,${data.segmented_image}`);
      } catch (error) {
        console.error("Error:", error);
        setErrorMessage("Failed to process the image. Please try again.");
      } finally {
        setIsLoading(false);
      }
    };

    reader.readAsDataURL(selectedFile);
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
            Upload MRI Scan
          </h1>
          <p className="mb-4 text-white text-center">
            Please upload an MRI image to see the segmented results.
          </p>
          {errorMessage && (
            <div
              className="alert alert-danger text-center mb-4 text-red-500"
              role="alert"
            >
              {errorMessage}
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

          <div className="mt-6 text-center">
            <h2 className="text-2xl font-bold mb-4 text-white">
              Segmented Image
            </h2>
            {segmentedImage && (
              <div className="flex justify-center items-center">
                <img
                  src={segmentedImage}
                  alt="Segmented"
                  className="border border-gray-300 rounded"
                  style={{
                    maxWidth: "100%",
                    height: "auto",
                  }}
                />
              </div>
            )}
          </div>
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

export default MriCancerPage;

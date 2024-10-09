"use client";
import { useState } from "react";
import Link from "next/link";
import Footer from "../components/Footer";

export default function Results() {
  const [submissionType, setSubmissionType] = useState(""); // 'image' or 'id'
  const [imageSrc, setImageSrc] = useState(null);

  // Placeholder function to simulate setting the submission type
  // In a real application, this would be set based on actual user actions
  const simulateSubmission = (type) => {
    setSubmissionType(type);
  };

  const handleImageUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setImageSrc(reader.result);
      };
      reader.readAsDataURL(file);
    }
  };

  return (
    <div className="bg-background-100 w-screen h-screen flex flex-col justify-center items-center relative">
      <div className="absolute bottom-9 right-12">
        <Link
          href="/"
          className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-700"
        >
          Homepage
        </Link>
      </div>
      <div className="flex items-center justify-center m-4">
        <h1 className="text-text-950 text-4xl">
          Medi<span className="font-bold text-accent-500">Scan</span>
        </h1>
      </div>
      <div className="flex flex-col items-center justify-center h-full w-full">
        {submissionType === "image" ? (
          <>
            <h2 className="text-white text-xl mb-2">
              Image Submitted Through Our Program
            </h2>
            {imageSrc && <img src={imageSrc} alt="Uploaded" className="mb-4" />}
            <p className="text-white text-lg mb-4">90% Unlikely</p>
          </>
        ) : (
          <>
            <h2 className="text-white text-xl mb-2">
              Image Through Our Program
            </h2>
            <p className="text-white text-lg mb-4">90% Unlikely</p>
          </>
        )}
      </div>
      <div className="mb-9">
        <Footer />
      </div>
      {/* Buttons to simulate submission type for demonstration purposes */}
      <div className="absolute top-4 left-4">
        <button
          onClick={() => simulateSubmission("image")}
          className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-700 mr-2"
        >
          Simulate Image Submission
        </button>
        <button
          onClick={() => simulateSubmission("id")}
          className="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-700"
        >
          Simulate ID Search
        </button>
        {submissionType === "image" && (
          <input
            type="file"
            accept="image/*"
            onChange={handleImageUpload}
            className="mt-4"
          />
        )}
      </div>
    </div>
  );
}

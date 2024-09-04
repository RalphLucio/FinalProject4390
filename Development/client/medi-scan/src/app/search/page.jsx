"use client";
import React, { useState } from "react";
import Footer from "../components/Footer";
import InputBox from "../components/InputBox";
import HomeButton from "../components/HomeButton";

export default function SearchViaID() {
  const [inputValue, setInputValue] = useState("");

  const handleInputChange = (e) => {
    setInputValue(e.target.value);
  };

  const handleSubmit = () => {
    // Handle the submit action here
    console.log("Submitted ID:", inputValue);
  };

  return (
    <div className="bg-background-100 w-screen h-screen flex flex-col justify-center items-center relative">
      <div className="absolute bottom-9 right-12">
        <HomeButton />
      </div>
      <div className="absolute top-4 left-1/2 transform -translate-x-1/2">
        <h1 className="text-text-950 text-3xl">
          Search Via <span className="font-bold text-accent-500">ID</span>
        </h1>
      </div>
      <div className="flex flex-col items-center justify-center h-full w-full">
        <div className="flex items-center justify-center space-x-1 mb-4">
          <InputBox
            type="text"
            placeholder="Enter ID"
            value={inputValue}
            onChange={handleInputChange}
            onSubmit={handleSubmit}
            buttonText="Search"
          />
        </div>
      </div>
      <div className="mt-auto mb-9">
        <Footer />
      </div>
    </div>
  );
}

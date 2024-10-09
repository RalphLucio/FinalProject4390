"use client";
import AccentButton from "./components/AccentButton";
import Footer from "./components/Footer";
import { useState } from "react";
import axios from "axios";
import Link from "next/link";

export default function Home() {
  const [data, setData] = useState({});

  const fetchData = async () => {
    try {
      const response = await axios.get("http://127.0.0.1:5000/data");
      setData(response.data);
    } catch (error) {
      console.log(error);
    }
  };

  return (
    <div className="bg-background-100 w-screen h-screen grid grid-cols-1 gap-4 content-between">
      <div className="flex items-center justify-center m-2">
        <h1 className="text-text-950 text-4xl">
          Medi<span className="font-bold text-accent-500">Scan</span>
        </h1>
      </div>
      <div className="flex justify-center p-4 bg-background-100 mt-2">
        <Link
          href="/mri-cancer"
          className="text-text-950 text-xl mx-4 p-2 border-2 border-accent-500 rounded-lg hover:bg-accent-500 hover:text-white transition duration-300"
        >
          MRI Cancer
        </Link>
        <Link
          href="/skin-cancer"
          className="text-text-950 text-xl mx-4 p-2 border-2 border-accent-500 rounded-lg hover:bg-accent-500 hover:text-white transition duration-300"
        >
          Skin Cancer
        </Link>
      </div>
      <div className="flex-grow"></div>
      <div className="mb-9">
        <Footer />
      </div>
    </div>
  );
}

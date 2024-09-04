"use client";
import AccentButton from "./components/AccentButton";
import Footer from "./components/Footer";
import SecondaryButton from "./components/SecondaryButton";
import { useState } from "react";
import axios from "axios";

export default function Home() {
  const signIn = "Sign In";
  const signUp = "Sign Up";

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
      <div></div>
      <div>
        <div className="flex items-center justify-center">
          <h1 className="text-text-950 text-2xl">
            Medi<span className="font-bold text-accent-500">Scan</span>
          </h1>
        </div>
        <div className="flex items-center justify-center">
          <SecondaryButton text={signUp} />
          <AccentButton text={signIn} />
        </div>
      </div>
      <div className="mb-9">
        <Footer />
      </div>
    </div>
  );
}

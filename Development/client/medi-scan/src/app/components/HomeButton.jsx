import React from "react";
import Link from "next/link";

const HomeButton = ({ buttonText = "HomePage", className = "" }) => {
  return (
    <Link
      href="/"
      className={`text-text-950 bg-accent-500 hover:bg-accent-600 font-medium rounded-lg text-sm px-5 py-2.5 me-2 mb-2  ${className}`}
    >
      {buttonText}
    </Link>
  );
};

export default HomeButton;

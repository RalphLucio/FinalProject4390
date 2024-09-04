import React from "react";

const InputBox = ({
  type = "text",
  placeholder = "",
  value,
  onChange,
  onSubmit,
  buttonText = "Submit",
  className = "",
}) => {
  return (
    <div className="flex items-center space-x-2">
      <input
        type={type}
        placeholder={placeholder}
        value={value}
        onChange={onChange}
        className={`border border-gray-300 rounded p-2 focus:outline-none focus:ring-2 focus:ring-accent-500 ${className}`}
      />
      <button
        onClick={onSubmit}
        className="bg-accent-500 text-white rounded p-2 hover:bg-accent-600 focus:outline-none focus:ring-2 focus:ring-accent-500"
      >
        {buttonText}
      </button>
    </div>
  );
};

export default InputBox;

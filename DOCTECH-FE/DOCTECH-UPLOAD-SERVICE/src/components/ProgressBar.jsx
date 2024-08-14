// src/components/ProgressBar.jsx

import React from 'react';

const ProgressBar = ({ progress }) => {
  return (
    <div className="w-full bg-gray-300 rounded-full h-2 mb-4">
      <div
        className="bg-green-500 h-2 rounded-full"
        style={{ width: `${progress}%` }}
      ></div>
    </div>
  );
};

export default ProgressBar;


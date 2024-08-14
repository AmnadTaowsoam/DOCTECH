import React, { useState } from "react";
import {
  FaCloudUploadAlt,
  FaFilePdf,
  FaFileImage,
  FaFileAlt,
  FaFolder,
  FaFile,
  FaArrowLeft,
  FaArrowRight,
} from "react-icons/fa";
import { ImUpload } from "react-icons/im";
import { uploadFile } from "../services/apiService";
import ProgressBar from "./ProgressBar";
import allowedFileTypes from '../utils/allowedFileTypes'; // นำเข้า allowedFileTypes

const FileUpload = () => {
  const [files, setFiles] = useState([]);
  const [uploadStatus, setUploadStatus] = useState([]);
  const [processMessage, setProcessMessage] = useState("");
  const [progress, setProgress] = useState(0);
  const [startIndex, setStartIndex] = useState(0); // Add state for the start index

  const handleFileChange = (e) => {
    // Clear previous files and status
    setFiles([]);
    setUploadStatus([]);

    const selectedFiles = [...e.target.files];
    const filteredFiles = selectedFiles.filter((file) =>
      allowedFileTypes.includes(file.type)
    );

    if (filteredFiles.length !== selectedFiles.length) {
      alert("บางไฟล์ถูกกรองออกไปเนื่องจากไม่ใช่ไฟล์ประเภทที่รองรับ");
    }

    setFiles(filteredFiles);
    setProcessMessage("Files selected. Ready to upload.");
    setProgress(0);
  };

  const handleUpload = async () => {
    setProcessMessage("Starting upload process...");
    const statusArray = [];
    for (const file of files) {
      try {
        statusArray.push({ name: file.name, status: "Uploading..." });
        setUploadStatus([...statusArray]);

        let uploadProgress = 0;
        const interval = setInterval(() => {
          uploadProgress += 10;
          setProgress(uploadProgress);
          if (uploadProgress >= 100) {
            clearInterval(interval);
          }
        }, 100);

        const response = await uploadFile(file);
        statusArray.pop();
        statusArray.push({ name: file.name, status: "Uploaded successfully" });
        setUploadStatus([...statusArray]);
        setProcessMessage(`${file.name} uploaded successfully.`);
      } catch (error) {
        statusArray.pop();
        statusArray.push({ name: file.name, status: "Failed to upload" });
        setUploadStatus([...statusArray]);
        setProcessMessage(`Failed to upload ${file.name}.`);
        setProgress(0);
      }
    }
    setProcessMessage("Upload process completed.");
  };

  const getFileIcon = (fileType) => {
    if (fileType.includes("pdf"))
      return <FaFilePdf className="text-red-500 w-6 h-6 mr-2" />;
    if (fileType.includes("image"))
      return <FaFileImage className="text-blue-500 w-6 h-6 mr-2" />;
    if (fileType.includes("word"))
      return <MdDescription className="text-blue-600 w-6 h-6 mr-2" />;
    return <FaFileAlt className="text-gray-500 w-6 h-6 mr-2" />;
  };

  // Function to move to the previous set of files
  const handlePrevious = () => {
    setStartIndex((prevIndex) => Math.max(prevIndex - 1, 0));
  };

  // Function to move to the next set of files
  const handleNext = () => {
    setStartIndex((prevIndex) =>
      Math.min(prevIndex + 1, Math.max(files.length - 3, 0))
    );
  };

  return (
    <div className="flex justify-center items-center min-h-screen bg-gradient-to-r">
      <div className="bg-white rounded-3xl shadow-2xl p-10 w-full max-w-2xl">
        <div className="flex flex-col items-center">
          <div className="text-4xl font-extrabold text-gray-900 text-center mb-6">
            Upload Your Files
          </div>

          <img
            src="/Filetype_3.png"
            alt="File Icon"
            className="mt-2 mb-2"
            style={{ width: "500px", height: "50px", borderRadius: "12px" }}
          />

          <div className="w-full border-dashed border-4 border-blue-400 rounded-lg p-8 mb-6 text-center bg-blue-50">
            <FaCloudUploadAlt className="text-blue-500 text-7xl mb-4 mx-auto" />
            <div className="text-gray-600 mb-2 text-lg">
              Drag & Drop your files here or
            </div>

            <div className="flex justify-center space-x-4">
              {/* Input for selecting individual files */}
              <input
                type="file"
                multiple
                onChange={handleFileChange}
                className="hidden"
                id="file-upload"
              />
              <label
                htmlFor="file-upload"
                className="btn bg-gradient-to-r from-blue-500 to-purple-500 text-white py-2 px-6 rounded-lg cursor-pointer hover:shadow-xl transform hover:scale-105 transition-transform duration-300 flex items-center"
              >
                <FaFile className="mr-1" /> Files
              </label>

              {/* Input for selecting a folder */}
              <input
                type="file"
                multiple
                webkitdirectory="true"
                onChange={handleFileChange}
                className="hidden"
                id="folder-upload"
              />
              <label
                htmlFor="folder-upload"
                className="btn bg-gradient-to-r from-green-500 to-teal-500 text-white py-2 px-6 rounded-lg cursor-pointer hover:shadow-xl transform hover:scale-105 transition-transform duration-300 flex items-center"
              >
                <FaFolder className="mr-1" /> Folder
              </label>
            </div>
          </div>

          {files.length > 0 && (
            <div className="w-full mb-2">
              {/* Display navigation buttons only if there are more than 3 files */}
              {files.length > 3 && (
                <div className="flex justify-between mb-2">
                  <button
                    onClick={handlePrevious}
                    disabled={startIndex === 0}
                    className="btn bg-gray-300 text-gray-700 px-4 py-2 rounded-lg"
                  >
                    <FaArrowLeft />
                  </button>
                  <button
                    onClick={handleNext}
                    disabled={startIndex + 3 >= files.length}
                    className="btn bg-gray-300 text-gray-700 px-4 py-2 rounded-lg"
                  >
                    <FaArrowRight />
                  </button>
                </div>
              )}

              {files.slice(startIndex, startIndex + 3).map((file, index) => (
                <div key={index} className="mb-2">
                  <div className="flex items-center mb-1">
                    {getFileIcon(file.type)}
                    <span className="flex-1 text-gray-700 font-semibold">
                      {file.name}
                    </span>
                  </div>
                  <ProgressBar progress={progress} />
                  <div className="ml-4 text-sm text-green-500 font-semibold">
                    {uploadStatus[index]?.status}
                  </div>
                </div>
              ))}
            </div>
          )}

          <button
            onClick={handleUpload}
            className="btn bg-gradient-to-r from-orange-400 to-yellow-500 text-white py-3 px-8 rounded-lg mt-2 shadow-lg transform hover:scale-105 transition-transform duration-300"
          >
            <ImUpload className="mr-1" />Upload
          </button>

          {processMessage && (
            <div className="mt-2 text-blue-700 text-center font-bold">
              {processMessage}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default FileUpload;

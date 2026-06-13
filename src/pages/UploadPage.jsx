import { useState } from "react";
import client from "../api/client";
import { useNavigate } from "react-router-dom";
import Navbar from "../components/Navbar";

export default function UploadPage() {
    
    const [file, setFile] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const navigate = useNavigate();

    const handleUpload = async () => {
  if (!file) return;

  const formData = new FormData();
  formData.append("file", file);

  setLoading(true);
  setError(null);

  try {
    const response = await client.post("/upload", formData);
    const fileId = response.data.file_id;
    navigate(`/dashboard/${fileId}`);
  } catch (err) {
    setError("Upload failed. Please try again.");
  } finally {
    setLoading(false);
  }
};
return (
  <div className="min-h-screen bg-gray-100">
    <Navbar />
    <div className="flex items-center justify-center py-20">
      <div className="bg-white p-10 rounded-2xl shadow-lg w-full max-w-lg text-center">
        <h2 className="text-2xl font-bold text-gray-800 mb-2">Upload your Financial Data</h2>
        <p className="text-gray-500 text-sm mb-6">Supports CSV, Excel and PDF files</p>
        <input
          type="file"
          accept=".csv,.xlsx,.xls,.pdf"
          onChange={(e) => setFile(e.target.files[0])}
          className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 mb-4"
        />
        {file && (
          <p className="text-sm text-gray-600 mb-4">
            Selected: <span className="font-medium text-blue-600">{file.name}</span>
          </p>
        )}
        <button
          onClick={handleUpload}
          disabled={!file || loading}
          className="w-full bg-blue-600 text-white py-3 rounded-xl font-semibold hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition"
        >
          {loading ? "Uploading..." : "Upload & Analyze"}
        </button>
        {error && <p className="mt-4 text-sm text-red-500">{error}</p>}
      </div>
    </div>
  </div>
);
}
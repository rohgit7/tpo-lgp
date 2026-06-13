import { useState } from "react";
import client from "../api/client";
import { useNavigate } from "react-router-dom";

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
    <div className="min-h-screen bg-gray-100 flex items-center justify-center">
  <div className="bg-white p-8 rounded-xl shadow-md w-full max-w-md">
    <h1 className="text-2xl font-bold text-center mb-6">Shakun AI</h1>
    <input
  type="file"
  accept=".csv,.xlsx,.xls,.pdf"
  onChange={(e) => setFile(e.target.files[0])}
  className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
/>
{file && (
  <p className="mt-3 text-sm text-gray-600">
    Selected: <span className="font-medium">{file.name}</span>
  </p>
)}
<button
  onClick={handleUpload}
  disabled={!file || loading}
  className="mt-6 w-full bg-blue-600 text-white py-2 rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
>
  {loading ? "Uploading..." : "Upload"}
</button>
{error && (
  <p className="mt-4 text-sm text-red-500 text-center">{error}</p>
)}

  </div>
</div>
  );
}
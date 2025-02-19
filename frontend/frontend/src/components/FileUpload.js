// components/FileUpload.js
import React, { useState } from 'react';

const FileUpload = ({ onUpload, loading }) => {
  const [file, setFile] = useState(null);
  const [message, setMessage] = useState('');

  const handleFileChange = (e) => {
    if (e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setMessage('Please select a file');
      return;
    }
    
    setMessage('Uploading...');
    const result = await onUpload(file);
    
    if (result && result.error) {
      setMessage(`Error: ${result.error}`);
    } else if (result && result.message) {
      setMessage(result.message);
      // Clear file input
      setFile(null);
      document.getElementById('file-input').value = '';
    }
  };

  return (
    <div className="flex flex-col space-y-2 sm:flex-row sm:space-y-0 sm:space-x-2 items-center">
      <input
        id="file-input"
        type="file"
        accept=".pdf"
        onChange={handleFileChange}
        className="border p-2 rounded"
      />
      <button
        onClick={handleUpload}
        disabled={!file || loading}
        className={`px-4 py-2 rounded-md ${
          loading || !file
            ? 'bg-gray-400 cursor-not-allowed'
            : 'bg-blue-600 hover:bg-blue-700 text-white'
        }`}
      >
        {loading ? 'Processing...' : 'Upload PDF'}
      </button>
      {message && (
        <span className="text-sm text-gray-600 ml-2">{message}</span>
      )}
    </div>
  );
};

export default FileUpload;
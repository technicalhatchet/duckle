import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Navbar from './components/Navbar';
import TransactionsTable from './components/TransactionsTable';
import FileUpload from './components/FileUpload';
import Categories from './components/Categories';
import './App.css';

function App() {
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Fetch transactions when component mounts
    fetchTransactions();
  }, []);

  const fetchTransactions = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:5000/api/transactions');
      if (!response.ok) {
        throw new Error('Failed to fetch transactions');
      }
      const data = await response.json();
      setTransactions(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (file) => {
    setLoading(true);
    setError(null);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('http://localhost:5000/api/upload-pdf', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to upload file');
      }

      const data = await response.json();
      // Reload transactions after successful upload
      fetchTransactions();
      return data;
    } catch (err) {
      setError(err.message);
      return { error: err.message };
    } finally {
      setLoading(false);
    }
  };

  const handleCategoryUpdate = async (transactionId, category, subcategory) => {
    try {
      const response = await fetch('http://localhost:5000/api/set-category', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          transaction_id: transactionId,
          category,
          subcategory,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to update category');
      }

      // Update the local state with the new category
      setTransactions(
        transactions.map(transaction => 
          transaction.id === transactionId
            ? { ...transaction, category, subcategory }
            : transaction
        )
      );

      return { success: true };
    } catch (err) {
      setError(err.message);
      return { error: err.message };
    }
  };

  const handleAddCategory = async (newCategory) => {
    try {
      const response = await fetch('http://localhost:5000/api/add-category', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          category: newCategory,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to add category');
      }

      return { success: true };
    } catch (err) {
      setError(err.message);
      return { error: err.message };
    }
  };

  const handleExport = () => {
    window.open('http://localhost:5000/api/export', '_blank');
  };

  return (
    <Router>
      <div className="App">
        <Navbar />
        <main className="container mx-auto px-4 py-8">
          <Routes>
            <Route
              path="/"
              element={
                <>
                  <div className="flex justify-between items-center mb-8">
                    <h1 className="text-3xl font-bold text-gray-800">Duckle - Bank Statement Parser</h1>
                    <div className="flex space-x-4">
                      <FileUpload onUpload={handleFileUpload} loading={loading} />
                      <button
                        onClick={handleExport}
                        disabled={transactions.length === 0}
                        className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        Export CSV
                      </button>
                    </div>
                  </div>
                  {error && (
                    <div className="mb-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded">
                      {error}
                    </div>
                  )}
                  <TransactionsTable
                    transactions={transactions}
                    loading={loading}
                    onCategoryUpdate={handleCategoryUpdate}
                  />
                </>
              }
            />
            <Route
              path="/categories"
              element={<Categories onAddCategory={handleAddCategory} />}
            />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
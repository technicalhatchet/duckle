// components/Categories.js
import React, { useState, useEffect } from 'react';

const Categories = ({ onAddCategory }) => {
  const [categories, setCategories] = useState([]);
  const [newCategory, setNewCategory] = useState('');
  const [message, setMessage] = useState('');
  
  useEffect(() => {
    fetchCategories();
  }, []);
  
  const fetchCategories = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/categories');
      if (response.ok) {
        const data = await response.json();
        setCategories(data);
      }
    } catch (error) {
      console.error('Failed to fetch categories:', error);
    }
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!newCategory.trim()) {
      setMessage('Category name cannot be empty');
      return;
    }
    
    const result = await onAddCategory(newCategory);
    
    if (result && result.success) {
      setMessage(`Category "${newCategory}" added successfully`);
      setNewCategory('');
      // Refresh categories
      fetchCategories();
    } else if (result && result.error) {
      setMessage(`Error: ${result.error}`);
    }
  };
  
  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">Manage Categories</h1>
      
      {/* Add new category form */}
      <div className="bg-white shadow-md rounded-lg p-6 mb-8">
        <h2 className="text-xl font-semibold mb-4">Add New Category</h2>
        <form onSubmit={handleSubmit} className="flex items-center">
          <input
            type="text"
            value={newCategory}
            onChange={(e) => setNewCategory(e.target.value)}
            className="flex-grow border border-gray-300 rounded-l px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Enter new category name"
          />
          <button
            type="submit"
            className="bg-blue-600 text-white px-4 py-2 rounded-r hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            Add
          </button>
        </form>
        {message && (
          <p className={`mt-2 text-sm ${message.includes('Error') ? 'text-red-600' : 'text-green-600'}`}>
            {message}
          </p>
        )}
      </div>
      
      {/* Categories list */}
      <div className="bg-white shadow-md rounded-lg p-6">
        <h2 className="text-xl font-semibold mb-4">Available Categories</h2>
        {categories.length === 0 ? (
          <p className="text-gray-500">No categories found</p>
        ) : (
          <ul className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {categories.map((category) => (
              <li 
                key={category} 
                className="bg-gray-100 p-3 rounded shadow-sm"
              >
                {category}
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
};

export default Categories;
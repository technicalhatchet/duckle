// components/CategorySelector.js
import React, { useState, useEffect } from 'react';

const CategorySelector = ({ transactionId, currentCategory, currentSubcategory, onCategoryChange }) => {
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    const fetchCategories = async () => {
      try {
        const response = await fetch('http://localhost:5000/api/categories');
        if (response.ok) {
          const data = await response.json();
          setCategories(data);
        }
      } catch (error) {
        console.error('Failed to fetch categories:', error);
      } finally {
        setLoading(false);
      }
    };
    
    fetchCategories();
  }, []);
  
  if (loading) {
    return <span>Loading...</span>;
  }
  
  const displayValue = currentSubcategory && currentSubcategory !== currentCategory 
    ? `${currentCategory} -> ${currentSubcategory}`
    : currentCategory;
  
  return (
    <select
      value={displayValue}
      onChange={(e) => onCategoryChange(transactionId, e.target.value)}
      className="border border-gray-300 rounded px-2 py-1 w-full"
    >
      <option value="">Select Category</option>
      {categories.map((category) => (
        <option key={category} value={category}>
          {category}
        </option>
      ))}
    </select>
  );
};

export default CategorySelector;
// components/TransactionsTable.js
import React, { useState, useEffect } from 'react';
import CategorySelector from './CategorySelector';

const TransactionsTable = ({ transactions, loading, onCategoryUpdate }) => {
  const [sortConfig, setSortConfig] = useState({ key: 'date', direction: 'ascending' });
  const [sortedTransactions, setSortedTransactions] = useState([]);

  useEffect(() => {
    let sorted = [...transactions];
    if (sortConfig.key) {
      sorted.sort((a, b) => {
        let aValue = a[sortConfig.key];
        let bValue = b[sortConfig.key];

        // Handle numeric values
        if (['amount', 'balance'].includes(sortConfig.key)) {
          aValue = parseFloat(aValue);
          bValue = parseFloat(bValue);
        }
        
        // Handle date values
        if (sortConfig.key === 'date') {
          aValue = new Date(aValue);
          bValue = new Date(bValue);
        }

        if (aValue < bValue) {
          return sortConfig.direction === 'ascending' ? -1 : 1;
        }
        if (aValue > bValue) {
          return sortConfig.direction === 'ascending' ? 1 : -1;
        }
        return 0;
      });
    }
    setSortedTransactions(sorted);
  }, [transactions, sortConfig]);

  const requestSort = (key) => {
    let direction = 'ascending';
    if (sortConfig.key === key && sortConfig.direction === 'ascending') {
      direction = 'descending';
    }
    setSortConfig({ key, direction });
  };

  const handleCategoryChange = async (transactionId, category) => {
    // Handle category updates with subcategory support
    let mainCategory = category;
    let subcategory = category;
    
    if (category.includes(' -> ')) {
      [mainCategory, subcategory] = category.split(' -> ');
    }
    
    await onCategoryUpdate(transactionId, mainCategory, subcategory);
  };

  if (loading) {
    return <div className="text-center py-4">Loading transactions...</div>;
  }

  if (!transactions.length) {
    return (
      <div className="text-center py-4 border rounded-lg bg-gray-100">
        No transactions found. Upload a bank statement to get started.
      </div>
    );
  }

  return (
    <div className="overflow-x-auto shadow-md rounded-lg">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            {['Date', 'Type', 'Details', 'Amount', 'Balance', 'Category'].map((header) => {
              const key = header.toLowerCase();
              return (
                <th
                  key={header}
                  onClick={() => requestSort(key === 'type' ? 'withdrawal_or_deposit' : key)}
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                >
                  <div className="flex items-center">
                    {header}
                    {sortConfig.key === (key === 'type' ? 'withdrawal_or_deposit' : key) && (
                      <span className="ml-1">
                        {sortConfig.direction === 'ascending' ? '↑' : '↓'}
                      </span>
                    )}
                  </div>
                </th>
              );
            })}
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Actions
            </th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {sortedTransactions.map((transaction) => (
            <tr 
              key={transaction.id}
              className={transaction.withdrawal_or_deposit === 'Deposit' ? 'bg-green-50' : ''}
            >
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                {transaction.date}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                {transaction.withdrawal_or_deposit}
              </td>
              <td className="px-6 py-4 text-sm text-gray-900">
                <div className="max-w-md truncate" title={transaction.details}>
                  {transaction.details}
                </div>
              </td>
              <td className={`px-6 py-4 whitespace-nowrap text-sm font-medium ${
                transaction.withdrawal_or_deposit === 'Deposit' 
                  ? 'text-green-600' 
                  : 'text-red-600'
              }`}>
                ${typeof transaction.amount === 'number' 
                  ? transaction.amount.toFixed(2) 
                  : parseFloat(transaction.amount).toFixed(2)}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                ${typeof transaction.balance === 'number' 
                  ? transaction.balance.toFixed(2) 
                  : parseFloat(transaction.balance).toFixed(2)}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                <CategorySelector
                  transactionId={transaction.id}
                  currentCategory={transaction.category}
                  currentSubcategory={transaction.subcategory}
                  onCategoryChange={handleCategoryChange}
                />
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <button className="text-blue-600 hover:text-blue-900">
                  View
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default TransactionsTable;
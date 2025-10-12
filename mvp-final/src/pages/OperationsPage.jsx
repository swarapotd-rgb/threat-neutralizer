import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Cookies from 'js-cookie';

const priorityColors = {
  'High': 'text-red-500',
  'Medium': 'text-yellow-500',
  'Low': 'text-green-500'
};

const statusColors = {
  'Active': 'bg-green-500',
  'Completed': 'bg-blue-500',
  'Suspended': 'bg-yellow-500',
  'Terminated': 'bg-red-500'
};

const OperationsPage = () => {
  const [operations, setOperations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedOperation, setSelectedOperation] = useState(null);
  const [loadingOperation, setLoadingOperation] = useState(false);
  const navigate = useNavigate();
  const username = Cookies.get("username");

  const handleLogout = () => {
    Cookies.remove("token");
    Cookies.remove("username");
    Cookies.remove("role");
    navigate("/");
  };

  const handleViewDetails = async (operation) => {
    setLoadingOperation(true);
    try {
      const token = Cookies.get('token');
      if (!token) {
        navigate('/login');
        return;
      }

      const response = await fetch(`http://localhost:8000/operations/${operation.operation_id}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch operation details');
      }

      const data = await response.json();
      setSelectedOperation(data.operation);
    } catch (err) {
      setError('Failed to load operation details: ' + err.message);
    } finally {
      setLoadingOperation(false);
    }
  };

  const handleBackToList = () => {
    setSelectedOperation(null);
    setError(null);
  };

  useEffect(() => {
    const fetchOperations = async () => {
      try {
        const token = Cookies.get('token');
        if (!token) {
          navigate('/login');
          return;
        }

        const response = await fetch('http://localhost:8000/operations', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });

        if (!response.ok) {
          throw new Error('Failed to fetch operations');
        }

        const data = await response.json();
        setOperations(data.operations);
        setLoading(false);
      } catch (err) {
        setError(err.message);
        setLoading(false);
      }
    };

    fetchOperations();
  }, [navigate]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 p-8">
        <div className="text-white text-center">Loading...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-900 p-8">
        <div className="text-red-500 text-center">{error}</div>
      </div>
    );
  }

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="min-h-screen bg-gray-900">
      {/* Navigation Bar */}
      <nav className="bg-gray-900 border-b border-gray-700 p-4 mb-8">
        <div className="container mx-auto flex justify-between items-center">
          <div className="flex items-center space-x-4">
            <button
              onClick={() => navigate('/home')}
              className="text-white hover:text-gray-300 transition-colors"
            >
              ← Back to Home
            </button>
            <h1 className="text-2xl font-bold text-white">Welcome, {username}!</h1>
          </div>
          <button
            onClick={handleLogout}
            className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors"
          >
            Logout
          </button>
        </div>
      </nav>

      <div className="p-8">
        {selectedOperation ? (
          <div className="container mx-auto">
            <div className="flex items-center mb-8">
              <button
                onClick={handleBackToList}
                className="text-white hover:text-gray-300 transition-colors flex items-center"
              >
                <span className="mr-2">←</span> Back to Operations
              </button>
            </div>

            {loadingOperation ? (
              <div className="text-white text-center">Loading operation details...</div>
            ) : (
              <div className="bg-gray-800 rounded-lg shadow-xl p-8 max-w-4xl mx-auto">
                {/* Operation Header */}
                <div className="mb-8">
                  <div className="flex justify-between items-start">
                    <div>
                      <h2 className="text-3xl font-bold text-white mb-2">
                        Operation {selectedOperation.code_name}
                      </h2>
                      <div className={`inline-block px-3 py-1 rounded-full text-white text-sm ${
                        statusColors[selectedOperation.status]}`}
                      >
                        {selectedOperation.status}
                      </div>
                    </div>
                    <div className={`text-lg font-semibold ${priorityColors[selectedOperation.priority]}`}>
                      {selectedOperation.priority} Priority
                    </div>
                  </div>
                </div>

                {/* Basic Information */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
                  <div className="bg-gray-700 rounded-lg p-6">
                    <h3 className="text-xl font-semibold text-white mb-4">Operation Details</h3>
                    <div className="space-y-3">
                      <p className="text-gray-300">ID: {selectedOperation.operation_id}</p>
                      <p className="text-gray-300">Status: {selectedOperation.status}</p>
                      <p className="text-gray-300">Start Date: {formatDate(selectedOperation.start_date)}</p>
                      {selectedOperation.end_date && (
                        <p className="text-gray-300">End Date: {formatDate(selectedOperation.end_date)}</p>
                      )}
                      <p className="text-gray-300">Classification: {selectedOperation.classified_level}</p>
                    </div>
                  </div>

                  <div className="bg-gray-700 rounded-lg p-6">
                    <h3 className="text-xl font-semibold text-white mb-4">Location & Personnel</h3>
                    {selectedOperation.target_location && (
                      <div className="mb-4">
                        <h4 className="text-lg font-semibold text-white mb-2">Target Location</h4>
                        <p className="text-gray-300">{selectedOperation.target_location.name}</p>
                        <p className="text-gray-300">Type: {selectedOperation.target_location.type}</p>
                      </div>
                    )}
                    <div>
                      <h4 className="text-lg font-semibold text-white mb-2">Involved Agents</h4>
                      <div className="space-y-2">
                        {selectedOperation.involved_agents.map((agent, index) => (
                          <div key={index} className="text-gray-300">
                            {agent.name} - {agent.rank}
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>

                {/* Description */}
                <div className="bg-gray-700 rounded-lg p-6 mb-8">
                  <h3 className="text-xl font-semibold text-white mb-4">Operation Description</h3>
                  <p className="text-gray-300 whitespace-pre-line">{selectedOperation.description}</p>
                </div>

                {/* Timeline */}
                <div className="bg-gray-700 rounded-lg p-6">
                  <h3 className="text-xl font-semibold text-white mb-4">Operation Timeline</h3>
                  <div className="space-y-4">
                    {selectedOperation.additional_info.timeline.map((event, index) => (
                      <div key={index} className="flex items-start">
                        <div className="w-32 flex-shrink-0">
                          <p className="text-gray-400">{formatDate(event.date)}</p>
                        </div>
                        <div className="ml-4">
                          <p className="text-white font-semibold">{event.event}</p>
                          <p className="text-gray-300">{event.details}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="container mx-auto">
            <h1 className="text-3xl font-bold text-white mb-8">Dates of Interest</h1>
            <div className="grid grid-cols-1 gap-6">
              {operations.map((operation) => (
                <div
                  key={operation.operation_id}
                  className="bg-gray-800 rounded-lg shadow-lg p-6 hover:shadow-2xl transition-all cursor-pointer"
                  onClick={() => handleViewDetails(operation)}
                >
                  <div className="flex justify-between items-start mb-4">
                    <div>
                      <h3 className="text-xl font-bold text-white">{operation.code_name}</h3>
                      <p className="text-gray-400">Operation #{operation.operation_id}</p>
                    </div>
                    <div className={`px-3 py-1 rounded-full text-white text-sm ${
                      statusColors[operation.status]}`}
                    >
                      {operation.status}
                    </div>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                    <div>
                      <p className="text-gray-400">Start Date:</p>
                      <p className="text-white">{formatDate(operation.start_date)}</p>
                    </div>
                    {operation.end_date && (
                      <div>
                        <p className="text-gray-400">End Date:</p>
                        <p className="text-white">{formatDate(operation.end_date)}</p>
                      </div>
                    )}
                  </div>
                  <div className="flex justify-between items-center mt-4">
                    <div className={`font-semibold ${priorityColors[operation.priority]}`}>
                      {operation.priority} Priority
                    </div>
                    <div className="text-blue-400 text-sm">
                      Click to view details →
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default OperationsPage;
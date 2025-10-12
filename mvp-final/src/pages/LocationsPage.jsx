import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Cookies from 'js-cookie';

// Color mappings for different location types and security levels
const typeColors = {
  'Weapon Cache': 'bg-red-500',
  'Cash Stash': 'bg-green-500',
  'Safe Room': 'bg-blue-500',
  'Intel Stash': 'bg-purple-500',
  'Medical Cache': 'bg-yellow-500'
};

const securityColors = {
  'high': 'border-red-500',
  'medium': 'border-yellow-500',
  'standard': 'border-green-500'
};

const LocationsPage = () => {
  const [locations, setLocations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedLocation, setSelectedLocation] = useState(null);
  const [loadingLocation, setLoadingLocation] = useState(false);
  const navigate = useNavigate();
  const username = Cookies.get("username");

  const handleLogout = () => {
    Cookies.remove("token");
    Cookies.remove("username");
    Cookies.remove("role");
    navigate("/");
  };

  const handleViewDetails = async (location) => {
    setLoadingLocation(true);
    try {
      const token = Cookies.get('token');
      if (!token) {
        navigate('/login');
        return;
      }

      const response = await fetch(`http://localhost:8000/locations/${location.location_id}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch location details');
      }

      const data = await response.json();
      setSelectedLocation(data.location);
    } catch (err) {
      setError('Failed to load location details: ' + err.message);
    } finally {
      setLoadingLocation(false);
    }
  };

  const handleBackToList = () => {
    setSelectedLocation(null);
    setError(null);
  };

  useEffect(() => {
    const fetchLocations = async () => {
      try {
        const token = Cookies.get('token');
        if (!token) {
          navigate('/login');
          return;
        }

        const response = await fetch('http://localhost:8000/locations', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });

        if (!response.ok) {
          throw new Error('Failed to fetch locations');
        }

        const data = await response.json();
        setLocations(data.locations);
        setLoading(false);
      } catch (err) {
        setError(err.message);
        setLoading(false);
      }
    };

    fetchLocations();
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
        {selectedLocation ? (
          <div className="container mx-auto">
            <div className="flex items-center mb-8">
              <button
                onClick={handleBackToList}
                className="text-white hover:text-gray-300 transition-colors flex items-center"
              >
                <span className="mr-2">←</span> Back to Locations
              </button>
            </div>

            {loadingLocation ? (
              <div className="text-white text-center">Loading location details...</div>
            ) : (
              <div className="bg-gray-800 rounded-lg shadow-xl p-8 max-w-4xl mx-auto">
                <div className="mb-8">
                  <h2 className="text-3xl font-bold text-white mb-4">{selectedLocation.name}</h2>
                  <div className={`inline-block px-3 py-1 rounded-full text-white text-sm mb-4 ${
                    typeColors[selectedLocation.type]}`}
                  >
                    {selectedLocation.type}
                  </div>
                </div>

                {/* Basic Information */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
                  <div className="bg-gray-700 rounded-lg p-6">
                    <h3 className="text-xl font-semibold text-white mb-4">Basic Information</h3>
                    <div className="space-y-3">
                      <p className="text-gray-300">ID: {selectedLocation.location_id}</p>
                      <p className="text-gray-300">Status: {selectedLocation.status}</p>
                      <p className="text-gray-300">Type: {selectedLocation.type}</p>
                      <p className="text-gray-300">Security Level: {selectedLocation.security_level}</p>
                    </div>
                  </div>

                  <div className="bg-gray-700 rounded-lg p-6">
                    <h3 className="text-xl font-semibold text-white mb-4">Access Information</h3>
                    <div className="space-y-3">
                      <p className="text-gray-300">Access Level: {selectedLocation.access_level}</p>
                      <p className="text-gray-300">Last Accessed: {selectedLocation.last_accessed || 'No record'}</p>
                    </div>
                  </div>
                </div>

                {/* Advanced Information */}
                <div className="bg-gray-700 rounded-lg p-6 mt-6">
                  <h3 className="text-xl font-semibold text-white mb-4">Advanced Information</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                    <div>
                      <h4 className="text-lg font-semibold text-white mb-2">Geolocation</h4>
                      <p className="text-gray-300">{selectedLocation.geolocation}</p>
                    </div>
                    <div>
                      <h4 className="text-lg font-semibold text-white mb-2">Contents</h4>
                      <p className="text-gray-300">{selectedLocation.contents}</p>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="container mx-auto">
            <h1 className="text-3xl font-bold text-white mb-8">Secure Locations</h1>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {locations.map((location) => (
                <div
                  key={location.location_id}
                  className={`bg-gray-800 rounded-lg shadow-lg p-6 border-2 ${securityColors[location.security_level]} hover:shadow-2xl transition-all cursor-pointer`}
                  onClick={() => handleViewDetails(location)}
                >
                  <div className={`w-full h-24 ${typeColors[location.type] || 'bg-gray-600'} rounded-lg flex items-center justify-center mb-4`}>
                    <span className="text-4xl">
                      {location.type === 'Weapon Cache' ? '🔫' :
                       location.type === 'Cash Stash' ? '💰' :
                       location.type === 'Safe Room' ? '🏰' :
                       location.type === 'Intel Stash' ? '📂' :
                       location.type === 'Medical Cache' ? '🏥' : '📍'}
                    </span>
                  </div>
                  <div className="text-white">
                    <h3 className="text-xl font-bold mb-2">{location.name}</h3>
                    <p className="text-gray-400 mb-1">Type: {location.type}</p>
                    <p className="text-gray-400 mb-1">Status: {location.status}</p>
                    <p className="text-gray-400">Security Level: {location.security_level}</p>
                  </div>
                  <div className="mt-4 text-blue-400 text-sm">
                    Click to view detailed information →
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

export default LocationsPage;
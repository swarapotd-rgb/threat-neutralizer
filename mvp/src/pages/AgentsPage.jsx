import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Cookies from 'js-cookie';

const AgentCard = ({ agent }) => {
  const [isFlipped, setIsFlipped] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [personalInfo, setPersonalInfo] = useState(null);
  const navigate = useNavigate();
  
  const statusColors = {
    'Active': 'bg-green-500',
    'On Leave': 'bg-yellow-500',
    'Training': 'bg-blue-500'
  };

  const handleFlip = async () => {
    if (!isFlipped && !personalInfo) {
      setIsLoading(true);
      try {
        const token = Cookies.get('token');
        if (!token) {
          navigate('/login');
          return;
        }

        const response = await fetch(`http://localhost:8000/agents/${agent.agent_number}`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });

        if (!response.ok) {
          throw new Error('Failed to fetch agent details');
        }

        const data = await response.json();
        setPersonalInfo(data.agent.personal_info);
      } catch (err) {
        console.error('Failed to load agent details:', err);
      } finally {
        setIsLoading(false);
      }
    }
    setIsFlipped(!isFlipped);
  };

  return (
    <div className="perspective w-96 h-[500px] m-4">
      <div 
        className={`relative w-full h-full duration-500 preserve-3d cursor-pointer ${
          isFlipped ? 'rotate-y-180' : ''
        }`}
        onClick={handleFlip}
      >
        {/* Front of the card */}
        <div className="absolute w-full h-full backface-hidden">
          <div className="bg-gray-800 rounded-lg shadow-lg p-6 h-full">
            <div className="relative h-48 mb-4">
              <img
                src={agent.photo_url || '/default-agent.jpg'}
                alt={agent.name}
                className="w-full h-full object-cover rounded-lg"
              />
              <div className={`absolute top-2 right-2 ${statusColors[agent.status] || 'bg-gray-500'} text-white px-3 py-1 rounded-full text-sm`}>
                {agent.status}
              </div>
            </div>
            <div className="text-white">
              <h3 className="text-xl font-bold mb-2">{agent.name}</h3>
              <p className="text-gray-400 mb-1">Agent #{agent.agent_number}</p>
              <p className="text-gray-400 mb-1">Rank: {agent.rank}</p>
              <p className="text-gray-400 mb-1">Clearance: {agent.clearance_level}</p>
              {agent.last_mission && (
                <p className="text-gray-400">Last Mission: {agent.last_mission}</p>
              )}
            </div>
            <div className="absolute bottom-4 left-0 right-0 text-center text-blue-400 text-sm">
              Click to view personal info →
            </div>
          </div>
        </div>

        {/* Back of the card */}
        <div className="absolute w-full h-full backface-hidden rotate-y-180">
          <div className="bg-gray-800 rounded-lg shadow-lg p-6 h-full">
            <h3 className="text-xl font-bold text-white mb-4">Personal Information</h3>
            {isLoading ? (
              <div className="flex items-center justify-center h-64">
                <div className="text-white">Loading personal details...</div>
              </div>
            ) : personalInfo ? (
              <div className="space-y-4">
                <div className="text-white">
                  <h4 className="text-lg font-semibold mb-2">Contact Details</h4>
                  <p className="text-gray-400">📱 Contact: {personalInfo.contact}</p>
                  <p className="text-gray-400">📍 Location: {personalInfo.location}</p>
                </div>

                <div className="text-white">
                  <h4 className="text-lg font-semibold mb-2">Professional Details</h4>
                  <p className="text-gray-400">🎯 Specialization: {personalInfo.specialization}</p>
                  <p className="text-gray-400">⏳ Years of Service: {personalInfo.years_of_service}</p>
                </div>

                <div className="text-white">
                  <h4 className="text-lg font-semibold mb-2">Current Status</h4>
                  <p className="text-gray-400">📋 Assignment: {personalInfo.current_assignment}</p>
                </div>

                <div className="text-white">
                  <h4 className="text-lg font-semibold mb-2">Certifications</h4>
                  <div className="flex flex-wrap gap-2">
                    {personalInfo.certifications.map((cert, index) => (
                      <span key={index} className="bg-gray-700 px-2 py-1 rounded-full text-sm">
                        {cert}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            ) : (
              <div className="flex items-center justify-center h-64">
                <div className="text-red-400">Failed to load personal details</div>
              </div>
            )}
            <div className="absolute bottom-4 left-0 right-0 text-center text-blue-400 text-sm">
              ← Click to view basic info
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

const AgentsPage = () => {
  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();
  const username = Cookies.get("username");
  
  const handleLogout = () => {
    Cookies.remove("token");
    Cookies.remove("username");
    Cookies.remove("role");
    navigate("/");
  };

  useEffect(() => {
    const fetchAgents = async () => {
      try {
        const token = Cookies.get('token');
        if (!token) {
          navigate('/login');
          return;
        }

        const response = await fetch('http://localhost:8000/agents', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });

        if (!response.ok) {
          throw new Error('Failed to fetch agents');
        }

        const data = await response.json();
        setAgents(data.agents);
        setLoading(false);
      } catch (err) {
        setError(err.message);
        setLoading(false);
      }
    };

    fetchAgents();
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
        <h1 className="text-3xl font-bold text-white mb-8">Agent Directory</h1>
        <div className="flex flex-wrap justify-center">
          {agents.map((agent) => (
            <AgentCard key={agent.agent_number} agent={agent} />
          ))}
        </div>
      </div>
    </div>
  );
};

export default AgentsPage;
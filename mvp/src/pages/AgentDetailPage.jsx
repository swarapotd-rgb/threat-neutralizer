import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Cookies from 'js-cookie';

const AgentDetailPage = () => {
  const [agentDetails, setAgentDetails] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const { agentId } = useParams();
  const navigate = useNavigate();

  useEffect(() => {
    const fetchAgentDetails = async () => {
      try {
        const token = Cookies.get('token');
        if (!token) {
          navigate('/login');
          return;
        }

        const response = await fetch(`http://localhost:8000/agents/${agentId}`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });

        if (!response.ok) {
          throw new Error('Failed to fetch agent details');
        }

        const data = await response.json();
        setAgentDetails(data.agent);
        setLoading(false);
      } catch (err) {
        setError(err.message);
        setLoading(false);
      }
    };

    fetchAgentDetails();
  }, [agentId, navigate]);

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

  if (!agentDetails) {
    return (
      <div className="min-h-screen bg-gray-900 p-8">
        <div className="text-white text-center">Agent not found or access denied</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 p-8">
      <div className="max-w-4xl mx-auto bg-gray-800 rounded-lg shadow-xl overflow-hidden">
        <div className="md:flex">
          <div className="md:flex-shrink-0">
            <img
              className="h-48 w-full object-cover md:w-48"
              src={agentDetails.photo_url || '/default-agent.jpg'}
              alt={agentDetails.name}
            />
          </div>
          <div className="p-8">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-sm text-gray-400">Agent #{agentDetails.agent_number}</div>
                <div className="text-2xl font-bold text-white mt-1">{agentDetails.name}</div>
              </div>
              <div className={`px-4 py-2 rounded-full text-sm ${
                agentDetails.status === 'Active' ? 'bg-green-500' :
                agentDetails.status === 'On Leave' ? 'bg-yellow-500' :
                'bg-blue-500'
              } text-white`}>
                {agentDetails.status}
              </div>
            </div>

            <div className="mt-6 border-t border-gray-700 pt-6">
              <div className="grid grid-cols-2 gap-6">
                <div>
                  <h3 className="text-lg font-semibold text-white mb-4">Agent Information</h3>
                  <div className="space-y-3">
                    <p className="text-gray-300">Rank: <span className="text-white">{agentDetails.rank}</span></p>
                    <p className="text-gray-300">Clearance: <span className="text-white">{agentDetails.clearance_level}</span></p>
                    <p className="text-gray-300">Last Mission: <span className="text-white">{agentDetails.last_mission}</span></p>
                  </div>
                </div>
                
                <div>
                  <h3 className="text-lg font-semibold text-white mb-4">Personal Information</h3>
                  <div className="space-y-3">
                    <p className="text-gray-300">Contact: <span className="text-white">{agentDetails.personal_info.contact}</span></p>
                    <p className="text-gray-300">Location: <span className="text-white">{agentDetails.personal_info.location}</span></p>
                    <p className="text-gray-300">Specialization: <span className="text-white">{agentDetails.personal_info.specialization}</span></p>
                    <p className="text-gray-300">Years of Service: <span className="text-white">{agentDetails.personal_info.years_of_service}</span></p>
                  </div>
                </div>
              </div>

              <div className="mt-6">
                <h3 className="text-lg font-semibold text-white mb-4">Certifications</h3>
                <div className="flex flex-wrap gap-2">
                  {agentDetails.personal_info.certifications.map((cert, index) => (
                    <span
                      key={index}
                      className="bg-gray-700 text-white px-3 py-1 rounded-full text-sm"
                    >
                      {cert}
                    </span>
                  ))}
                </div>
              </div>

              <div className="mt-6">
                <h3 className="text-lg font-semibold text-white mb-2">Current Assignment</h3>
                <p className="text-gray-300">{agentDetails.personal_info.current_assignment}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AgentDetailPage;
import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import Cookies from "js-cookie";

const HomePage = () => {
  const [activeTab, setActiveTab] = useState("files");
  const [username, setUsername] = useState("");
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    const storedUsername = Cookies.get("username");
    if (storedUsername) {
      setUsername(storedUsername);
    } else {
      navigate("/");
    }
  }, [navigate]);

  const handleLogout = () => {
    Cookies.remove("token");
    Cookies.remove("username");
    Cookies.remove("role");
    navigate("/");
  };

  const fetchClassifiedFiles = async () => {
    setLoading(true);
    setError("");
    try {
      const token = Cookies.get("token");
      if (!token) {
        handleLogout();
        return;
      }

      const response = await fetch("/api/files", {
        method: "GET",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        if (response.status === 401) {
          handleLogout();
          return;
        }
        throw new Error("Failed to fetch files");
      }

      const data = await response.json();
      setFiles(data.files);
    } catch (err) {
      setError("Error loading classified files");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (activeTab === "files") {
      fetchClassifiedFiles();
    }
  }, [activeTab]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-black to-gray-800">
      {/* Navigation Bar */}
      <nav className="bg-gray-900 border-b border-gray-700 p-4">
        <div className="container mx-auto flex justify-between items-center">
          <div className="flex items-center space-x-4">
            <h1 className="text-2xl font-bold text-white">Hello, {username}!</h1>
          </div>
          <button
            onClick={handleLogout}
            className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors"
          >
            Logout
          </button>
        </div>
      </nav>

      {/* Tab Navigation */}
      <div className="container mx-auto mt-6 px-4">
        <div className="flex space-x-4 border-b border-gray-700">
          <button
            className={`px-4 py-2 text-white ${
              activeTab === "files"
                ? "border-b-2 border-indigo-500 font-bold"
                : "text-gray-400 hover:text-white"
            }`}
            onClick={() => setActiveTab("files")}
          >
            Classified Files
          </button>
          <button
            className={`px-4 py-2 text-white ${
              activeTab === "personal"
                ? "border-b-2 border-indigo-500 font-bold"
                : "text-gray-400 hover:text-white"
            }`}
            onClick={() => navigate('/agents')}
          >
            Personal Information
          </button>
          <button
            className={`px-4 py-2 text-white ${
              activeTab === "locations"
                ? "border-b-2 border-indigo-500 font-bold"
                : "text-gray-400 hover:text-white"
            }`}
            onClick={() => navigate('/locations')}
          >
            Secured Locations
          </button>
          <button
            className={`px-4 py-2 text-white ${
              activeTab === "dates"
                ? "border-b-2 border-indigo-500 font-bold"
                : "text-gray-400 hover:text-white"
            }`}
            onClick={() => navigate('/operations')}
          >
            Dates of Interest
          </button>
        </div>

        {/* Content Area */}
        <div className="mt-6">
          {activeTab === "files" && (
            <div>
              <h2 className="text-2xl font-bold text-white mb-4">Classified Files</h2>
              {loading ? (
                <div className="text-white">Loading...</div>
              ) : error ? (
                <div className="text-red-500">{error}</div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {files.map((file) => (
                    <div
                      key={file.file_id}
                      className="bg-gray-800 p-4 rounded-lg border border-gray-700 hover:border-indigo-500 transition-colors"
                    >
                      <h3 className="text-lg font-semibold text-white mb-2">
                        {file.filename}
                      </h3>
                      <p className="text-gray-400 text-sm mb-3">ID: {file.file_id}</p>
                      <button
                        onClick={async () => {
                          try {
                            const token = Cookies.get("token");
                            const response = await fetch(`/api/files/${file.file_id}`, {
                              headers: {
                                Authorization: `Bearer ${token}`,
                              },
                            });
                            
                            if (!response.ok) {
                              throw new Error("Failed to download file");
                            }
                            
                            const blob = await response.blob();
                            const url = window.URL.createObjectURL(blob);
                            const a = document.createElement("a");
                            a.href = url;
                            a.download = file.filename;
                            document.body.appendChild(a);
                            a.click();
                            window.URL.revokeObjectURL(url);
                            document.body.removeChild(a);
                          } catch (err) {
                            console.error("Download error:", err);
                            setError("Error downloading file");
                          }
                        }}
                        className="w-full px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg transition-colors text-sm font-medium"
                      >
                        Download File
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
          {/* Removed personal tab content since it now redirects */}
          {/* Locations page is now a separate route */}
          {activeTab === "dates" && (
            <div className="text-white">
              <p>Redirecting to Operations...</p>
              {navigate('/operations')}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default HomePage;

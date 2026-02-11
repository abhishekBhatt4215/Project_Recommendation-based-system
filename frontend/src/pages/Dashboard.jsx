import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../services/api";

const Dashboard = () => {
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const accessToken = localStorage.getItem("access_token");
    if (!accessToken) {
      navigate("/login");
      return;
    }

    const fetchDashboard = async () => {
      try {
        const response = await api.get("dashboard/overview/");
        setData(response.data);
      } catch (err) {
        setError("Failed to load dashboard data.");
      } finally {
        setLoading(false);
      }
    };

    fetchDashboard();
  }, [navigate]);

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    setIsLoggedIn(false);   // ✅ important
    navigate("/login");
  };

  if (loading) {
    return <div className="text-center mt-20 text-xl">Loading...</div>;
  }

  if (error) {
    return <div className="text-center mt-20 text-red-600">{error}</div>;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-12 px-4">
      <div className="max-w-6xl mx-auto">
        <div className="flex justify-between items-center mb-12">
          <h1 className="text-4xl font-bold text-gray-800">
            Welcome, {data.username}
          </h1>
          <button
            onClick={handleLogout}
            className="px-6 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition duration-300 font-semibold"
          >
            Logout
          </button>
        </div>

        {/* Quick Stats Section */}
        <div className="bg-white rounded-lg shadow-lg p-8">
          <h3 className="text-2xl font-bold text-gray-800 mb-6">
            Quick Stats
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="text-3xl font-bold text-indigo-600">
                {data.total_trips}
              </div>
              <p className="text-gray-600">Trips Planned</p>
            </div>

            <div className="text-center">
              <div className="text-3xl font-bold text-indigo-600">
                {data.ai_interactions}
              </div>
              <p className="text-gray-600">AI Interactions</p>
            </div>

            <div className="text-center">
              <div className="text-3xl font-bold text-indigo-600">
                {new Date(data.member_since).toLocaleDateString()}
              </div>
              <p className="text-gray-600">Member Since</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;

import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../services/api";

const Profile = () => {
  const navigate = useNavigate();
  const [profile, setProfile] = useState(null);
  const [dashboardStats, setDashboardStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!localStorage.getItem("access_token")) {
      navigate("/login");
    }
  }, [navigate]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const profileRes = await api.get("profile/me/");
        const dashboardRes = await api.get("dashboard/overview/");

        setProfile(profileRes.data);
        setDashboardStats(dashboardRes.data);
      } catch (err) {
        console.error("Profile fetch error:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-lg text-gray-600">Loading profile...</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-12 px-4">
      <div className="max-w-4xl mx-auto">

        {/* Profile Card */}
        <div className="bg-white rounded-2xl shadow-xl p-10">

          {/* Header */}
          <div className="flex items-center gap-6 mb-10">
            <div className="w-20 h-20 rounded-full bg-indigo-600 text-white flex items-center justify-center text-3xl font-bold">
              {dashboardStats?.username?.charAt(0).toUpperCase()}
            </div>

            <div>
              <h1 className="text-3xl font-bold text-gray-800">
                {dashboardStats?.username}
              </h1>
              <p className="text-gray-500">
                Member since{" "}
                {new Date(dashboardStats?.member_since).toLocaleDateString()}
              </p>
            </div>
          </div>

          {/* Info Section */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">

            <div>
              <p className="text-sm text-gray-500">Username</p>
              <p className="text-lg font-semibold text-gray-800">
                {profile?.username}
              </p>
            </div>

            <div>
              <p className="text-sm text-gray-500">Email</p>
              <p className="text-lg font-semibold text-gray-800">
                {profile?.email}
              </p>
            </div>

          </div>

          {/* Stats Section */}
          <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6">

            <div className="bg-indigo-50 rounded-xl p-6 text-center">
              <p className="text-3xl font-bold text-indigo-600">
                {dashboardStats?.total_trips}
              </p>
              <p className="text-gray-600 mt-2">Trips Planned</p>
            </div>

            <div className="bg-indigo-50 rounded-xl p-6 text-center">
              <p className="text-3xl font-bold text-indigo-600">
                {dashboardStats?.ai_interactions}
              </p>
              <p className="text-gray-600 mt-2">AI Interactions</p>
            </div>

            <div className="bg-indigo-50 rounded-xl p-6 text-center">
              <p className="text-3xl font-bold text-indigo-600">
                {new Date(dashboardStats?.member_since).getFullYear()}
              </p>
              <p className="text-gray-600 mt-2">Member Since</p>
            </div>

          </div>

        </div>
      </div>
    </div>
  );
};

export default Profile;

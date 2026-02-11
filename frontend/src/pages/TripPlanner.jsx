import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import ReactMarkdown from 'react-markdown';

const TripPlanner = () => {
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    origin_city: '',
    destination_city: '',
    depart_date: '',
    return_date: '',
    passengers: 1,
    cabin_class: 'economy',
    interests: '',
    days: 1,
    max_budget: '',
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [response, setResponse] = useState(null);

  // Proper authentication redirect
  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      navigate('/login');
    }
  }, [navigate]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setResponse(null);
    setLoading(true);

    if (
      !formData.origin_city ||
      !formData.destination_city ||
      !formData.depart_date ||
      !formData.return_date ||
      !formData.interests ||
      !formData.max_budget
    ) {
      setError('Please fill in all required fields.');
      setLoading(false);
      return;
    }

    try {
      const payload = {
        ...formData,
        passengers: parseInt(formData.passengers),
        days: parseInt(formData.days),
        max_budget: parseFloat(formData.max_budget),
      };

      const result = await api.post('ai/plan_trip/', payload);
      setResponse(result.data);
    } catch (err) {
      if (err.response && err.response.data) {
        setError(err.response.data.detail || 'Failed to plan trip.');
      } else {
        setError('Network error. Please check your connection.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-12 px-4">
      <div className="max-w-6xl mx-auto">

        {/* Header */}
        <div className="mb-12">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">Trip Planner</h1>
          <p className="text-gray-600 text-lg">
            Plan your perfect trip with AI assistance
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">

          {/* ================= FORM SECTION ================= */}
          <div className="lg:col-span-2">
            <form
              onSubmit={handleSubmit}
              className="bg-white rounded-lg shadow-lg p-8 space-y-6"
            >
              {error && (
                <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
                  <p className="text-red-700 font-semibold">{error}</p>
                </div>
              )}

              {/* Origin City */}
              <div>
                <label className="block font-semibold mb-2">
                  Origin City *
                </label>
                <input
                  type="text"
                  name="origin_city"
                  value={formData.origin_city}
                  onChange={handleInputChange}
                  className="w-full px-4 py-2 border rounded-lg"
                />
              </div>

              {/* Destination City */}
              <div>
                <label className="block font-semibold mb-2">
                  Destination City *
                </label>
                <input
                  type="text"
                  name="destination_city"
                  value={formData.destination_city}
                  onChange={handleInputChange}
                  className="w-full px-4 py-2 border rounded-lg"
                />
              </div>

              {/* Dates */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block font-semibold mb-2">
                    Departure Date *
                  </label>
                  <input
                    type="date"
                    name="depart_date"
                    value={formData.depart_date}
                    onChange={handleInputChange}
                    className="w-full px-4 py-2 border rounded-lg"
                  />
                </div>
                <div>
                  <label className="block font-semibold mb-2">
                    Return Date *
                  </label>
                  <input
                    type="date"
                    name="return_date"
                    value={formData.return_date}
                    onChange={handleInputChange}
                    className="w-full px-4 py-2 border rounded-lg"
                  />
                </div>
              </div>

              {/* Passengers + Cabin */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block font-semibold mb-2">
                    Passengers
                  </label>
                  <input
                    type="number"
                    name="passengers"
                    value={formData.passengers}
                    onChange={handleInputChange}
                    min="1"
                    className="w-full px-4 py-2 border rounded-lg"
                  />
                </div>
                <div>
                  <label className="block font-semibold mb-2">
                    Cabin Class
                  </label>
                  <select
                    name="cabin_class"
                    value={formData.cabin_class}
                    onChange={handleInputChange}
                    className="w-full px-4 py-2 border rounded-lg"
                  >
                    <option value="economy">Economy</option>
                    <option value="business">Business</option>
                  </select>
                </div>
              </div>

              {/* Interests */}
              <div>
                <label className="block font-semibold mb-2">
                  Interests *
                </label>
                <textarea
                  name="interests"
                  value={formData.interests}
                  onChange={handleInputChange}
                  rows="3"
                  className="w-full px-4 py-2 border rounded-lg"
                />
              </div>

              {/* Duration + Budget */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block font-semibold mb-2">
                    Duration (days)
                  </label>
                  <input
                    type="number"
                    name="days"
                    value={formData.days}
                    onChange={handleInputChange}
                    className="w-full px-4 py-2 border rounded-lg"
                  />
                </div>
                <div>
                  <label className="block font-semibold mb-2">
                    Max Budget *
                  </label>
                  <input
                    type="number"
                    name="max_budget"
                    value={formData.max_budget}
                    onChange={handleInputChange}
                    className="w-full px-4 py-2 border rounded-lg"
                  />
                </div>
              </div>

              {/* Submit Button */}
              <button
                type="submit"
                disabled={loading}
                className="w-full py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-bold rounded-lg"
              >
                {loading ? 'Planning Trip...' : 'Plan My Trip 🌍'}
              </button>
            </form>
          </div>

          {/* ================= RESPONSE SECTION ================= */}
          <div className="lg:col-span-1">
            {response && (
              <div className="bg-white rounded-xl shadow-xl p-8 sticky top-8 max-h-[80vh] overflow-y-auto">
                <h2 className="text-2xl font-bold text-indigo-700 mb-6">
                  ✨ AI Travel Plan
                </h2>

                <div className="prose prose-sm max-w-none">
                  <ReactMarkdown>
                    {typeof response === 'string'
                      ? response
                      : JSON.stringify(response, null, 2)}
                  </ReactMarkdown>
                </div>

                <button
                  onClick={() => setResponse(null)}
                  className="w-full mt-6 py-2 bg-gray-200 rounded-lg"
                >
                  Clear Result
                </button>
              </div>
            )}
          </div>

        </div>
      </div>
    </div>
  );
};

export default TripPlanner;

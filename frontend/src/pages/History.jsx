import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import ReactMarkdown from 'react-markdown';

const History = () => {
  const navigate = useNavigate();
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [expandedId, setExpandedId] = useState(null);
  const [error, setError] = useState('');

  // Redirect if not logged in
  useEffect(() => {
    if (!localStorage.getItem('access_token')) {
      navigate('/login');
    }
  }, [navigate]);

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const res = await api.get('ai/history/');
        setHistory(res.data);
      } catch (err) {
        setError('Failed to load history.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchHistory();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-lg text-gray-600">Loading history...</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-12 px-4">
      <div className="max-w-5xl mx-auto">

        <h1 className="text-3xl font-bold text-gray-800 mb-8">
            AI Trip History
        </h1>

        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-red-700">{error}</p>
          </div>
        )}

        {history.length === 0 && (
          <div className="bg-white p-6 rounded-lg shadow text-center">
            <p className="text-gray-600">
              You haven’t generated any trips yet.
            </p>
          </div>
        )}

        <div className="space-y-6">
          {history.map((item) => (
            <div
              key={item.id}
              className="bg-white rounded-xl shadow-lg p-6"
            >
              <div className="flex justify-between items-start">
                <div>
                  <p className="text-sm text-gray-500">
                    {new Date(item.created_at).toLocaleString()}
                  </p>
                  <p className="font-semibold text-gray-800 mt-1">
                    Prompt:
                  </p>
                  <p className="text-gray-700 text-sm">
                    {item.prompt}
                  </p>
                </div>

                <button
                  onClick={() =>
                    setExpandedId(
                      expandedId === item.id ? null : item.id
                    )
                  }
                  className="px-4 py-1 bg-indigo-600 text-white text-sm rounded-lg hover:bg-indigo-700 transition"
                >
                  {expandedId === item.id ? 'Hide' : 'View'}
                </button>
              </div>

              {expandedId === item.id && (
                <div className="mt-6 border-t pt-4 prose max-w-none text-gray-700">
                  <ReactMarkdown>
                    {item.ai_response}
                  </ReactMarkdown>
                </div>
              )}
            </div>
          ))}
        </div>

      </div>
    </div>
  );
};

export default History;

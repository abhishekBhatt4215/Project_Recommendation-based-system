import { Link } from "react-router-dom";

const Home = () => {
  const isLoggedIn = !!localStorage.getItem("access_token");

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">

      {/* HERO SECTION */}
      <section className="max-w-6xl mx-auto px-6 py-24 text-center">
        
        <h1 className="text-5xl md:text-6xl font-bold text-gray-900 leading-tight">
          Plan Your Perfect Trip <br />
          <span className="text-indigo-600">With AI Assistance ✨</span>
        </h1>

        <p className="mt-6 text-lg text-gray-600 max-w-2xl mx-auto">
          Smart itineraries, budget optimization, flight suggestions, and personalized travel plans —
          all generated in seconds.
        </p>

        <div className="mt-10 flex justify-center gap-6">
          {isLoggedIn ? (
            <Link
              to="/trip-planner"
              className="px-8 py-3 bg-indigo-600 text-white rounded-xl font-semibold hover:bg-indigo-700 transition duration-300"
            >
              Plan a Trip
            </Link>
          ) : (
            <>
              <Link
                to="/signup"
                className="px-8 py-3 bg-indigo-600 text-white rounded-xl font-semibold hover:bg-indigo-700 transition duration-300"
              >
                Get Started
              </Link>

              <Link
                to="/login"
                className="px-8 py-3 bg-white text-indigo-600 border border-indigo-600 rounded-xl font-semibold hover:bg-indigo-50 transition duration-300"
              >
                Login
              </Link>
            </>
          )}
        </div>      
      </section>
            {/* DETAILED FEATURES SECTION */}
      <section className="py-24 bg-gradient-to-br from-blue-50 to-indigo-100">
        <div className="max-w-6xl mx-auto px-6">

          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900">
              Why Choose TravelAI?
            </h2>
            <p className="text-gray-600 mt-4 max-w-2xl mx-auto">
              Powerful AI technology combined with smart travel planning tools
              to give you the perfect experience.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-10">

            {/* Card 1 */}
            <div className="bg-white rounded-2xl shadow-lg p-8 hover:shadow-xl transition duration-300">
              <h3 className="text-2xl font-semibold text-indigo-600 mb-4">
                🤖 AI Itinerary Generation
              </h3>
              <p className="text-gray-600">
                Enter your travel details and let our AI instantly generate a
                detailed day-by-day itinerary tailored to your interests.
              </p>
            </div>

            {/* Card 2 */}
            <div className="bg-white rounded-2xl shadow-lg p-8 hover:shadow-xl transition duration-300">
              <h3 className="text-2xl font-semibold text-indigo-600 mb-4">
                💰 Budget-Conscious Planning
              </h3>
              <p className="text-gray-600">
                Our system intelligently considers your budget constraints
                and optimizes travel recommendations accordingly.
              </p>
            </div>

            {/* Card 3 */}
            <div className="bg-white rounded-2xl shadow-lg p-8 hover:shadow-xl transition duration-300">
              <h3 className="text-2xl font-semibold text-indigo-600 mb-4">
                📜 Trip History Tracking
              </h3>
              <p className="text-gray-600">
                Access and review all your previously generated trips anytime
                with a clean and organized history view.
              </p>
            </div>

            {/* Card 4 */}
            <div className="bg-white rounded-2xl shadow-lg p-8 hover:shadow-xl transition duration-300">
              <h3 className="text-2xl font-semibold text-indigo-600 mb-4">
                🔐 Secure Authentication
              </h3>
              <p className="text-gray-600">
                JWT-based secure authentication ensures your travel plans and
                account data remain private and protected.
              </p>
            </div>

          </div>

        </div>
      </section>
            {/* FINAL CTA SECTION */}
      <section className="bg-indigo-600 py-24 text-center">
        <div className="max-w-4xl mx-auto px-6">

          <h2 className="text-4xl font-bold text-white mb-6">
            Ready to Plan Your Next Adventure?
          </h2>

          <p className="text-indigo-100 text-lg mb-10">
            Let AI handle the planning while you focus on enjoying the journey.
          </p>

          {isLoggedIn ? (
            <Link
              to="/trip-planner"
              className="px-10 py-4 bg-white text-indigo-600 rounded-xl font-semibold hover:bg-gray-100 transition duration-300"
            >
              Start Planning 🌍
            </Link>
          ) : (
            <Link
              to="/signup"
              className="px-10 py-4 bg-white text-indigo-600 rounded-xl font-semibold hover:bg-gray-100 transition duration-300"
            >
              Create Free Account
            </Link>
          )}

        </div>
      </section>



    </div>
  );
};

export default Home;

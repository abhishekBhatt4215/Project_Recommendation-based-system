import { Link, useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";

function Navbar({ isLoggedIn, setIsLoggedIn }) {
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    setIsLoggedIn(!!token);
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    setIsLoggedIn(false);
    navigate("/login");
  };

  return (
    <nav className="bg-white shadow-md px-6 py-4 flex justify-between items-center">
      <h1 className="text-xl font-bold text-blue-600">
        AI Travel Planner
      </h1>

      <div className="space-x-6">
        <Link to="/" className="hover:text-blue-600">
          Home
        </Link>

        {isLoggedIn ? (
          <>
            <Link to="/dashboard" className="hover:text-blue-600">
              Dashboard
            </Link>
            <Link to="/history">History</Link>

            <Link to="/profile" className="hover:text-blue-600">
              Profile
            </Link>

            <button
              onClick={handleLogout}
              className="text-red-600 font-semibold"
            >
              Logout
            </button>
          </>
        ) : (
          <>
            <Link to="/login" className="hover:text-blue-600">
              Login
            </Link>

            <Link to="/signup" className="hover:text-blue-600">
              Signup
            </Link>
          </>
        )}
      </div>
    </nav>
  );
}

export default Navbar;

import { useNavigate } from "react-router-dom";

function Register() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <div className="bg-white rounded-2xl shadow-xl p-10 w-[420px]">

        <h1 className="text-4xl font-bold text-green-700 text-center">
          🌞 Solar Safe
        </h1>

        <p className="text-center text-gray-500 mt-2">
          Edge AI Powered PV Fault Detection
        </p>

        <h2 className="text-2xl font-semibold text-center mt-8">
          Create Account
        </h2>

        <p className="text-center text-gray-500 mb-6">
          Register to continue
        </p>

        <label className="block font-medium mb-2">
          Full Name
        </label>

        <input
          type="text"
          placeholder="Enter your full name"
          className="w-full border border-gray-300 rounded-lg p-3 mb-4"
        />

        <label className="block font-medium mb-2">
          Email Address
        </label>

        <input
          type="email"
          placeholder="Enter your email"
          className="w-full border border-gray-300 rounded-lg p-3 mb-4"
        />

        <label className="block font-medium mb-2">
          Password
        </label>

        <input
          type="password"
          placeholder="Enter your password"
          className="w-full border border-gray-300 rounded-lg p-3 mb-4"
        />

        <label className="block font-medium mb-2">
          Confirm Password
        </label>

        <input
          type="password"
          placeholder="Confirm your password"
          className="w-full border border-gray-300 rounded-lg p-3"
        />

        <button
          onClick={() => navigate("/")}
          className="w-full bg-green-600 text-white py-3 rounded-lg mt-6 hover:bg-green-700"
        >
          Register
        </button>

        <p className="text-center mt-6 text-gray-600">
          Already have an account?{" "}
          <span
            onClick={() => navigate("/")}
            className="text-green-600 font-semibold cursor-pointer hover:underline"
          >
            Login
          </span>
        </p>

      </div>
    </div>
  );
}

export default Register;
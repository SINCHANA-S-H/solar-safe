import { useNavigate } from "react-router-dom";
function Login() {
    const navigate = useNavigate();

  return (
    <div className="min-h-screen flex items-center justify-center bg-sky blue-100">

      <div className="bg-white rounded-2xl shadow-xl p-10 w-[420px]">

        <h1 className="text-5xl font-bold text-lavender-700 text-center">
          SolarSafe AI Portal
        </h1>

        <p className="text-center text-lavender-500 mt-3">
          Edge AI Powered PV Fault Detection
        </p>

        <h2 className="text-3xl font-semibold text-center mt-8">
          Welcome Back
        </h2>

        <p className="text-center text-lavender-500 mb-8">
          Login to continue
        </p>

        {/* Email */}

        <label className="block font-medium mb-2">
          Email Address
        </label>

        <input
          type="email"
          placeholder="Enter your email"
          className="w-full border border-gray-300 rounded-lg p-3 mb-6"
        />

        {/* Password */}

        <label className="block font-medium mb-2">
          Password
        </label>

        <input
          type="password"
          placeholder="Enter your password"
          className="w-full border border-gray-300 rounded-lg p-3"
        />
<button
  onClick={() => navigate("/dashboard")}
  className="w-full bg-green-600 text-white py-3 rounded-lg mt-6 hover:bg-green-700 transition"
>
  Login
</button>
<p className="text-center mt-6 text-lavender-500">
  Don't have an account?{" "}
  <a
    href="/register"
    className="text-lavender-600 font-semibold hover:underline"
  >
    Register
  </a>
</p>
      </div>

    </div>
  );
}

export default Login;
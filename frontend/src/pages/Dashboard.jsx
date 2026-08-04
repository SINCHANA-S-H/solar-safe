function Dashboard() {
  return (
    <div className="min-h-screen bg-gray-100">

      {/* Navbar */}

      <div className="bg-green-700 text-white p-5 text-2xl font-bold">
        🌞 Solar Safe Dashboard
      </div>

      {/* Main Layout */}

      <div className="flex">

        {/* Sidebar */}

        <div className="w-64 bg-white h-screen shadow-md p-5">

          <h2 className="font-bold text-xl mb-6">
            Menu
          </h2>

          <ul className="space-y-4">

            <li>🏠 Dashboard</li>

            <li>📤 Upload</li>

            <li>📜 History</li>

            <li>📄 Reports</li>

            <li>🗺 Solar Map</li>

            <li>⚙ Settings</li>

          </ul>

        </div>

        {/* Main Content */}

        <div className="flex-1 p-8">

          <h1 className="text-3xl font-bold">
            Dashboard
          </h1>

          <p className="text-gray-600 mt-2">
            Welcome to Solar Safe
          </p>

        </div>

      </div>

    </div>
  );
}

export default Dashboard;
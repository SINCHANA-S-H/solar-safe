import { useState } from "react";
import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "../../context/useAuth";
import Sidebar from "./Sidebar";
import Navbar from "./Navbar";
import ChatBot from "../chatbot/ChatBot";

export default function ProtectedRoute() {
  const { isAuthenticated, loading } = useAuth();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 flex flex-col items-center justify-center p-4">
        <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-emerald-600 to-amber-500 flex items-center justify-center animate-spin text-white shadow-lg shadow-emerald-600/20 mb-4">
          <div className="w-4 h-4 bg-white rounded-full" />
        </div>
        <p className="text-slate-600 font-medium text-sm animate-pulse">
          Loading Solar Safe...
        </p>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/" replace />;
  }

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex">
      {/* Sidebar */}
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      {/* Main Content Area */}
      <div className="flex-1 lg:pl-72 flex flex-col min-w-0">
        <Navbar onOpenSidebar={() => setSidebarOpen(true)} />
        <main className="flex-1 p-4 sm:p-6 lg:p-8 max-w-7xl w-full mx-auto">
          <Outlet />
        </main>
      </div>

      {/* Global Floating Chatbot Assistant */}
      <ChatBot />
    </div>
  );
}

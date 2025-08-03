import React from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
  useLocation,
} from "react-router-dom";
import { AuthProvider, useAuth } from "./contexts/AuthContext";
import { AuthPage } from "./components/auth/AuthPage";
import { Dashboard } from "./components/dashboard/Dashboard";
import { Header } from "./components/common/Header";
import { LandingPage } from "./components/landing/LandingPage";

const AppRoutes: React.FC = () => {
  const { isAuthenticated } = useAuth();
  const location = useLocation();
  const showHeader = isAuthenticated && location.pathname !== "/";

  return (
    <>
      {showHeader && <Header />}
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route
          path="/auth"
          element={
            isAuthenticated ? <Navigate to="/dashboard" /> : <AuthPage />
          }
        />
        <Route
          path="/dashboard"
          element={isAuthenticated ? <Dashboard /> : <Navigate to="/auth" />}
        />
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </>
  );
};

function App() {
  return (
    <AuthProvider>
      <Router>
        <AppRoutes />
      </Router>
    </AuthProvider>
  );
}

export default App;

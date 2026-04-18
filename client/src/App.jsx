import { useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import Navbar from './components/Navbar';
import Dashboard from './pages/Dashboard';
import ProductDetail from './pages/ProductDetail';
import Login from './pages/Login';
import Signup from './pages/Signup';

export default function App() {
  const [searchQuery, setSearchQuery] = useState('');

  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/* Public routes — no Navbar */}
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />

          {/* Protected routes — with Navbar */}
          <Route
            path="/*"
            element={
              <ProtectedRoute>
                <Navbar onSearch={setSearchQuery} />
                <Routes>
                  <Route path="/" element={<Dashboard searchQuery={searchQuery} />} />
                  <Route path="/product/:productId" element={<ProductDetail />} />
                  <Route path="*" element={<Navigate to="/" replace />} />
                </Routes>
              </ProtectedRoute>
            }
          />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

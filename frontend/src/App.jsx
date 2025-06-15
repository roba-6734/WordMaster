import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from  './context/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import Layout from './components/Layout';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import DashboardPage from './pages/DashboardPage';
import WordsPage from './pages/WordsPage';
import './App.css';

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          {/* Public routes */}
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          
          {/* Protected routes */}
          <Route path="/dashboard" element={
            <ProtectedRoute>
              <Layout>
                <DashboardPage />
              </Layout>
            </ProtectedRoute>
          } />
          
          {/* Placeholder routes for future pages */}
          <Route path="/words" element={
            <ProtectedRoute>
              <Layout>
                <WordsPage />
              </Layout>
            </ProtectedRoute>
          } />
          
          <Route path="/study" element={
            <ProtectedRoute>
              <Layout>
                <div className="container mx-auto p-6">
                  <h1 className="text-3xl font-bold">Study Session</h1>
                  <p className="text-muted-foreground mt-2">Coming soon...</p>
                </div>
              </Layout>
            </ProtectedRoute>
          } />
          
          <Route path="/quiz" element={
            <ProtectedRoute>
              <Layout>
                <div className="container mx-auto p-6">
                  <h1 className="text-3xl font-bold">Quiz</h1>
                  <p className="text-muted-foreground mt-2">Coming soon...</p>
                </div>
              </Layout>
            </ProtectedRoute>
          } />
          
          <Route path="/progress" element={
            <ProtectedRoute>
              <Layout>
                <div className="container mx-auto p-6">
                  <h1 className="text-3xl font-bold">Progress</h1>
                  <p className="text-muted-foreground mt-2">Coming soon...</p>
                </div>
              </Layout>
            </ProtectedRoute>
          } />
          
          {/* Default redirect */}
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          
          {/* Catch all route */}
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;

import { Suspense, lazy } from 'react'
import { Route, Routes } from 'react-router-dom'
import Navbar from './components/Navbar'
import ProtectedRoute from './components/ProtectedRoute'

// 路由 lazy load：縮小首屏 bundle、加快載入
const Dashboard = lazy(() => import('./pages/Dashboard'))
const ForgotPassword = lazy(() => import('./pages/ForgotPassword'))
const History = lazy(() => import('./pages/History'))
const ItineraryDetail = lazy(() => import('./pages/ItineraryDetail'))
const Login = lazy(() => import('./pages/Login'))
const Pikmin = lazy(() => import('./pages/Pikmin'))
const Register = lazy(() => import('./pages/Register'))
const ResendVerification = lazy(() => import('./pages/ResendVerification'))
const ResetPassword = lazy(() => import('./pages/ResetPassword'))
const VerifyEmail = lazy(() => import('./pages/VerifyEmail'))

function PageFallback() {
  return (
    <div className="flex items-center justify-center py-24">
      <span className="spinner" />
    </div>
  )
}

export default function App() {
  return (
    <div className="min-h-screen">
      <Navbar />
      <Suspense fallback={<PageFallback />}>
        <Routes>
          {/* 公開頁面 */}
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/verify-email" element={<VerifyEmail />} />
          <Route path="/forgot-password" element={<ForgotPassword />} />
          <Route path="/reset-password" element={<ResetPassword />} />
          <Route path="/resend-verification" element={<ResendVerification />} />

          {/* 需登入 */}
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/history"
            element={
              <ProtectedRoute>
                <History />
              </ProtectedRoute>
            }
          />
          <Route
            path="/pikmin"
            element={
              <ProtectedRoute>
                <Pikmin />
              </ProtectedRoute>
            }
          />
          <Route
            path="/itinerary/:id"
            element={
              <ProtectedRoute>
                <ItineraryDetail />
              </ProtectedRoute>
            }
          />
        </Routes>
      </Suspense>
    </div>
  )
}

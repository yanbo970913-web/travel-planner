import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function Navbar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  function handleLogout() {
    logout()
    navigate('/login')
  }

  return (
    <nav className="bg-white border-b border-slate-200 shadow-sm">
      <div className="max-w-5xl mx-auto px-4 h-14 flex items-center justify-between">
        <Link to="/" className="font-bold text-brand-600 text-lg">
          ✈️ 行程規劃系統
        </Link>
        <div className="flex items-center gap-4 text-sm">
          {user ? (
            <>
              <Link to="/" className="hover:text-brand-600">
                規劃行程
              </Link>
              <Link to="/history" className="hover:text-brand-600">
                歷史行程
              </Link>
              <Link to="/pikmin" className="hover:text-lime-600">
                🌸 皮克敏
              </Link>
              <span className="text-slate-400 hidden sm:inline">{user.email}</span>
              <button
                onClick={handleLogout}
                className="text-slate-500 hover:text-red-500"
              >
                登出
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className="hover:text-brand-600">
                登入
              </Link>
              <Link
                to="/register"
                className="bg-brand-600 text-white px-3 py-1.5 rounded-md hover:bg-brand-700"
              >
                註冊
              </Link>
            </>
          )}
        </div>
      </div>
    </nav>
  )
}

import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function Navbar() {
  const { user, logout, deleteAccount } = useAuth()
  const navigate = useNavigate()
  const [open, setOpen] = useState(false)

  function handleLogout() {
    logout()
    setOpen(false)
    navigate('/login')
  }

  async function handleDelete() {
    if (!confirm('確定要刪除帳號嗎？所有歷史行程將一併刪除，無法復原。')) return
    try {
      await deleteAccount()
      setOpen(false)
      navigate('/register')
    } catch {
      alert('刪除失敗，請稍後再試')
    }
  }

  const links = user ? (
    <>
      <Link to="/" className="btn-ghost px-3 py-1.5" onClick={() => setOpen(false)}>
        規劃行程
      </Link>
      <Link to="/history" className="btn-ghost px-3 py-1.5" onClick={() => setOpen(false)}>
        歷史行程
      </Link>
      <Link
        to="/pikmin"
        className="btn-ghost px-3 py-1.5 text-lime-300 hover:text-lime-200"
        onClick={() => setOpen(false)}
      >
        🌸 皮克敏
      </Link>
      <span className="hidden lg:inline text-slate-500 text-sm px-2">{user.email}</span>
      <button onClick={handleLogout} className="btn-ghost px-3 py-1.5 hover:text-red-400">
        登出
      </button>
      <button onClick={handleDelete} className="btn-ghost px-3 py-1.5 text-slate-500 hover:text-red-400">
        刪除帳號
      </button>
    </>
  ) : (
    <>
      <Link to="/login" className="btn-ghost px-3 py-1.5" onClick={() => setOpen(false)}>
        登入
      </Link>
      <Link to="/register" className="btn-primary px-4 py-1.5" onClick={() => setOpen(false)}>
        註冊
      </Link>
    </>
  )

  return (
    <nav className="sticky top-0 z-30 bg-slate-950/70 backdrop-blur-md border-b border-slate-800">
      <div className="max-w-5xl mx-auto px-4 h-14 flex items-center justify-between">
        <Link to="/" className="font-bold text-lg bg-gradient-to-r from-brand-400 to-lime-300 bg-clip-text text-transparent">
          ✈️ 行程規劃系統
        </Link>

        {/* 桌面選單 */}
        <div className="hidden sm:flex items-center gap-1 text-sm">{links}</div>

        {/* 手機漢堡 */}
        <button
          className="sm:hidden btn-ghost px-2 py-1.5"
          onClick={() => setOpen((o) => !o)}
          aria-label="選單"
        >
          {open ? '✕' : '☰'}
        </button>
      </div>

      {/* 手機展開選單 */}
      {open && (
        <div className="sm:hidden border-t border-slate-800 px-4 py-3 flex flex-col gap-1 text-sm">
          {links}
        </div>
      )}
    </nav>
  )
}

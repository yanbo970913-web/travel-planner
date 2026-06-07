import { createContext, useContext, useEffect, useState } from 'react'
import client from '../api/client'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  // 啟動時若有 token，嘗試載入使用者
  useEffect(() => {
    const token = localStorage.getItem('access_token')
    if (!token) {
      setLoading(false)
      return
    }
    client
      .get('/users/me')
      .then((res) => setUser(res.data))
      .catch(() => localStorage.removeItem('access_token'))
      .finally(() => setLoading(false))
  }, [])

  async function login(email, password) {
    // 後端 login 用 OAuth2 表單格式，username 帶 email
    const form = new URLSearchParams()
    form.append('username', email)
    form.append('password', password)
    const res = await client.post('/auth/login', form, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    })
    localStorage.setItem('access_token', res.data.access_token)
    const me = await client.get('/users/me')
    setUser(me.data)
  }

  function logout() {
    localStorage.removeItem('access_token')
    setUser(null)
  }

  async function deleteAccount() {
    await client.delete('/users/me')
    logout()
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, logout, deleteAccount }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  return useContext(AuthContext)
}

import { useEffect } from 'react'
import { useLocation } from 'react-router-dom'

const TITLES = {
  '/': '規劃行程',
  '/login': '登入',
  '/register': '註冊',
  '/verify-email': '信箱驗證',
  '/forgot-password': '忘記密碼',
  '/reset-password': '重設密碼',
  '/resend-verification': '重寄驗證信',
  '/history': '歷史行程',
  '/pikmin': '皮克敏探索',
}

const BASE = '自動化行程規劃系統'

// 依路由動態更新瀏覽器分頁標題
export default function RouteTitle() {
  const { pathname } = useLocation()
  useEffect(() => {
    const sub = TITLES[pathname] || (pathname.startsWith('/itinerary/') ? '行程詳情' : '')
    document.title = sub ? `${sub}・${BASE}` : BASE
  }, [pathname])
  return null
}

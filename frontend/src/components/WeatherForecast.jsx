import { useEffect, useState } from 'react'
import client from '../api/client'

// 目的地每日天氣預報（資料來源 Open-Meteo，免費免金鑰）。
// 自動載入；任何失敗都只顯示一行淡淡的說明，絕不讓頁面壞掉。
export default function WeatherForecast({ location, startDate, days }) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!location) return
    let alive = true
    setLoading(true)
    client
      .get('/weather', {
        params: { location, start_date: startDate || undefined, days: days || 1 },
        // 天氣為次要資訊：給較短逾時，避免後端冷啟動時 spinner 永遠轉
        timeout: 25000,
      })
      .then((res) => alive && setData(res.data))
      .catch(
        () =>
          alive &&
          setData({ available: false, note: '天氣服務暫時無法使用，稍後再試。', daily: [] }),
      )
      .finally(() => alive && setLoading(false))
    return () => {
      alive = false
    }
  }, [location, startDate, days])

  if (loading) {
    return (
      <div className="rounded-2xl border border-sky-800/40 bg-sky-950/20 p-4 text-sm text-sky-300/80 inline-flex items-center gap-2">
        <span className="spinner" /> 載入「{location}」天氣預報中…
      </div>
    )
  }

  // 查不到 / 超出預報範圍 / 服務暫時不可用 → 只顯示淡淡一行，不打擾使用者
  if (!data || !data.available || !data.daily?.length) {
    if (!data?.note) return null
    return (
      <div className="rounded-2xl border border-slate-800 bg-slate-900/40 p-3 text-xs text-slate-500">
        🌤️ {data.note}
      </div>
    )
  }

  function fmtDate(iso) {
    const [y, m, d] = (iso || '').split('-').map(Number)
    if (!y || !m || !d) return iso
    return new Date(y, m - 1, d).toLocaleDateString('zh-TW', {
      month: 'numeric',
      day: 'numeric',
      weekday: 'short',
    })
  }
  function temp(t) {
    return t == null ? '—' : `${Math.round(t)}°`
  }

  return (
    <div className="rounded-2xl border border-sky-800/40 bg-sky-950/20 p-5 animate-fade-in">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-bold text-sky-300">
          🌤️ {data.resolved_name || location} 天氣預報
        </h3>
        <span className="text-xs text-sky-500/80">Open-Meteo</span>
      </div>

      <div className="flex gap-3 overflow-x-auto pb-1">
        {data.daily.map((d) => (
          <div
            key={d.date}
            className="flex-shrink-0 w-24 rounded-xl bg-slate-900/60 border border-slate-800 p-3 text-center"
          >
            <div className="text-xs text-slate-400">{fmtDate(d.date)}</div>
            <div className="text-3xl my-1 leading-none" title={d.description}>
              {d.emoji}
            </div>
            <div className="text-[11px] text-slate-400 truncate" title={d.description}>
              {d.description}
            </div>
            <div className="text-sm mt-1">
              <span className="text-rose-300 font-medium">{temp(d.temp_max)}</span>
              <span className="text-slate-600"> / </span>
              <span className="text-sky-300">{temp(d.temp_min)}</span>
            </div>
            {d.precipitation_probability != null && (
              <div className="text-[11px] text-sky-400/90 mt-0.5">
                💧 {d.precipitation_probability}%
              </div>
            )}
          </div>
        ))}
      </div>

      {data.note && <p className="text-xs text-slate-500 mt-2">※ {data.note}</p>}
    </div>
  )
}

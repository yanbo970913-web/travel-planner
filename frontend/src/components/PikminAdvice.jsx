import { useState } from 'react'
import client, { apiError } from '../api/client'

// 可重用的皮克敏資訊面板：傳入 location，點按鈕後載入並顯示。
// 同時用於獨立查詢頁與行程詳情頁（融入行程）。
export default function PikminAdvice({ location, autoLoad = false }) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [loaded, setLoaded] = useState(false)

  async function load() {
    if (!location) return
    setLoading(true)
    setError('')
    try {
      const res = await client.get('/pikmin/advice', { params: { location } })
      setData(res.data)
      setLoaded(true)
    } catch (err) {
      setError(apiError(err, '皮克敏資訊載入失敗'))
    } finally {
      setLoading(false)
    }
  }

  // autoLoad 時於首次渲染載入
  if (autoLoad && !loaded && !loading && !error) {
    load()
  }

  if (!loaded) {
    return (
      <div className="bg-lime-50 border border-lime-200 rounded-xl p-4">
        <button
          onClick={load}
          disabled={loading || !location}
          className="text-sm font-medium text-lime-700 hover:text-lime-900 disabled:opacity-60"
        >
          {loading
            ? '🌱 載入皮克敏資訊中…'
            : `🌸 查看「${location}」的特別皮克敏（玩家專用）`}
        </button>
        {error && <p className="text-sm text-red-600 mt-2">{error}</p>}
      </div>
    )
  }

  return (
    <div className="bg-lime-50 border border-lime-200 rounded-xl p-5 space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="font-bold text-lime-800">🌸 {data.location} 皮克敏情報</h3>
        <span className="text-xs text-lime-600">每日更新 · {data.date}</span>
      </div>

      {data.regional_pikmin?.length > 0 && (
        <div>
          <div className="text-sm font-semibold text-lime-700 mb-1">
            🗺️ 地區限定 / 特別皮克敏
          </div>
          <div className="flex flex-wrap gap-2">
            {data.regional_pikmin.map((p, i) => (
              <span
                key={i}
                className="text-xs bg-white border border-lime-300 rounded-full px-2.5 py-1"
              >
                {p}
              </span>
            ))}
          </div>
        </div>
      )}

      {data.decor_highlights?.length > 0 && (
        <div>
          <div className="text-sm font-semibold text-lime-700 mb-1">
            🎀 各地點可獲得的裝飾皮克敏
          </div>
          <ul className="text-sm text-slate-700 space-y-0.5">
            {data.decor_highlights.map((d, i) => (
              <li key={i}>
                <span className="font-medium">{d.place_type}</span>：{d.decor}
              </li>
            ))}
          </ul>
        </div>
      )}

      {data.current_events?.length > 0 && (
        <div>
          <div className="text-sm font-semibold text-lime-700 mb-1">
            📅 近期活動皮克敏
          </div>
          <ul className="text-sm text-slate-700 list-disc list-inside space-y-0.5">
            {data.current_events.map((e, i) => (
              <li key={i}>{e}</li>
            ))}
          </ul>
        </div>
      )}

      {data.tips && (
        <p className="text-sm text-lime-800 bg-lime-100 rounded-md p-3">
          💡 {data.tips}
        </p>
      )}

      <p className="text-xs text-slate-400">
        ※ 活動資訊由 AI 依其知識生成，可能非當下官方最新公告，請以遊戲內為準。
      </p>
    </div>
  )
}

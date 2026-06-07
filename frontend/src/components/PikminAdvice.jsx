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
      <div className="rounded-2xl border border-lime-800/50 bg-lime-950/30 p-4">
        <button
          onClick={load}
          disabled={loading || !location}
          className="text-sm font-medium text-lime-300 hover:text-lime-200 disabled:opacity-60 inline-flex items-center gap-2"
        >
          {loading ? (
            <>
              <span className="spinner" /> 載入皮克敏資訊中…
            </>
          ) : (
            `🌸 查看「${location}」的特別皮克敏（玩家專用）`
          )}
        </button>
        {error && <p className="text-sm text-red-300 mt-2">{error}</p>}
      </div>
    )
  }

  return (
    <div className="rounded-2xl border border-lime-800/50 bg-lime-950/30 p-5 space-y-4 animate-fade-in">
      <div className="flex items-center justify-between">
        <h3 className="font-bold text-lime-300">🌸 {data.location} 皮克敏情報</h3>
        <span className="text-xs text-lime-500">每日更新 · {data.date}</span>
      </div>

      {data.regional_pikmin?.length > 0 && (
        <div>
          <div className="text-sm font-semibold text-lime-400 mb-1.5">
            🗺️ 地區限定 / 特別皮克敏
          </div>
          <div className="flex flex-wrap gap-2">
            {data.regional_pikmin.map((p, i) => (
              <span
                key={i}
                className="text-xs rounded-full px-2.5 py-1 bg-lime-900/40 border border-lime-700/50 text-lime-200"
              >
                {p}
              </span>
            ))}
          </div>
        </div>
      )}

      {data.decor_highlights?.length > 0 && (
        <div>
          <div className="text-sm font-semibold text-lime-400 mb-1.5">
            🎀 各地點可獲得的裝飾皮克敏
          </div>
          <ul className="text-sm text-slate-300 space-y-0.5">
            {data.decor_highlights.map((d, i) => (
              <li key={i}>
                <span className="font-medium text-slate-200">{d.place_type}</span>：{d.decor}
              </li>
            ))}
          </ul>
        </div>
      )}

      {data.current_events?.length > 0 && (
        <div>
          <div className="text-sm font-semibold text-lime-400 mb-1.5">📅 近期活動皮克敏</div>
          <ul className="text-sm text-slate-300 list-disc list-inside space-y-0.5">
            {data.current_events.map((e, i) => (
              <li key={i}>{e}</li>
            ))}
          </ul>
        </div>
      )}

      {data.tips && (
        <p className="text-sm text-lime-200 bg-lime-900/30 rounded-lg p-3">💡 {data.tips}</p>
      )}

      <p className="text-xs text-slate-500">
        ※ 活動資訊由 AI 依其知識生成，可能非當下官方最新公告，請以遊戲內為準。
      </p>
    </div>
  )
}

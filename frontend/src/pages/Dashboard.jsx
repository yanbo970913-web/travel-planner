import { useState } from 'react'
import client, { apiError } from '../api/client'
import ItineraryForm from '../components/ItineraryForm'
import ItineraryView from '../components/ItineraryView'
import PikminAdvice from '../components/PikminAdvice'

export default function Dashboard() {
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function handleGenerate(payload) {
    setError('')
    setResult(null)
    setLoading(true)
    try {
      const res = await client.post('/itineraries/generate', payload)
      setResult(res.data)
    } catch (err) {
      setError(apiError(err, 'AI 生成失敗，請稍後再試'))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-5xl mx-auto px-4 py-8 animate-fade-in">
      <h1 className="text-3xl font-bold mb-1 text-white">規劃你的旅程</h1>
      <p className="text-slate-400 mb-6">
        輸入目的地與偏好，AI 會為你排定每日行程與交通動線。
      </p>

      <div className="grid md:grid-cols-2 gap-8 items-start">
        <ItineraryForm onSubmit={handleGenerate} loading={loading} />

        <div>
          {error && <div className="alert-error mb-4">{error}</div>}
          {loading && (
            <div className="card p-10 text-center text-slate-400">
              <span className="spinner mb-3" />
              <div>AI 正在規劃行程，請稍候…</div>
            </div>
          )}
          {result ? (
            <>
              <div className="alert-success mb-4">已產生並儲存到你的歷史行程！</div>
              <ItineraryView itinerary={result} />
              <div className="mt-6">
                <PikminAdvice location={result.location} />
              </div>
            </>
          ) : (
            !loading && <div className="empty">行程結果會顯示在這裡</div>
          )}
        </div>
      </div>
    </div>
  )
}

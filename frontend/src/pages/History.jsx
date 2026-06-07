import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import client, { apiError } from '../api/client'

export default function History() {
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  function load() {
    setLoading(true)
    client
      .get('/itineraries')
      .then((res) => setItems(res.data))
      .catch((err) => setError(apiError(err)))
      .finally(() => setLoading(false))
  }

  useEffect(load, [])

  async function handleDelete(id) {
    if (!confirm('確定要刪除這筆行程嗎？')) return
    try {
      await client.delete(`/itineraries/${id}`)
      setItems((list) => list.filter((it) => it.id !== id))
    } catch (err) {
      alert(apiError(err, '刪除失敗'))
    }
  }

  return (
    <div className="max-w-3xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-6">歷史行程</h1>
      {error && (
        <div className="text-sm text-red-600 bg-red-50 rounded-md p-3 mb-4">
          {error}
        </div>
      )}
      {loading ? (
        <p className="text-slate-500">載入中…</p>
      ) : items.length === 0 ? (
        <div className="text-center text-slate-400 py-12 border-2 border-dashed border-slate-200 rounded-xl">
          還沒有任何行程，
          <Link to="/" className="text-brand-600">
            去規劃一個吧
          </Link>
        </div>
      ) : (
        <ul className="space-y-3">
          {items.map((it) => (
            <li
              key={it.id}
              className="bg-white border border-slate-200 rounded-lg p-4 flex items-center justify-between"
            >
              <Link to={`/itinerary/${it.id}`} className="flex-1">
                <div className="font-semibold text-brand-700">{it.title}</div>
                <div className="text-sm text-slate-500">
                  {it.location} · {it.days} 天 ·{' '}
                  {new Date(it.created_at).toLocaleDateString()}
                </div>
              </Link>
              <button
                onClick={() => handleDelete(it.id)}
                className="text-slate-400 hover:text-red-500 text-sm ml-4"
              >
                刪除
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}

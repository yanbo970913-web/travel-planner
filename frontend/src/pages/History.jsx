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
    <div className="max-w-3xl mx-auto px-4 py-8 animate-fade-in">
      <h1 className="text-3xl font-bold mb-6 text-white">歷史行程</h1>
      {error && <div className="alert-error mb-4">{error}</div>}
      {loading ? (
        <div className="flex justify-center py-16">
          <span className="spinner" />
        </div>
      ) : items.length === 0 ? (
        <div className="empty">
          還沒有任何行程，
          <Link to="/" className="link">
            去規劃一個吧
          </Link>
        </div>
      ) : (
        <ul className="space-y-3">
          {items.map((it) => (
            <li
              key={it.id}
              className="card p-4 flex items-center justify-between hover:border-brand-600/60 transition"
            >
              <Link to={`/itinerary/${it.id}`} className="flex-1">
                <div className="font-semibold text-brand-300">{it.title}</div>
                <div className="text-sm text-slate-400">
                  {it.location} · {it.days} 天 ·{' '}
                  {new Date(it.created_at).toLocaleDateString()}
                </div>
              </Link>
              <button
                onClick={() => handleDelete(it.id)}
                className="text-slate-500 hover:text-red-400 text-sm ml-4"
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

import { useState } from 'react'
import PikminAdvice from '../components/PikminAdvice'

export default function Pikmin() {
  const [input, setInput] = useState('')
  const [query, setQuery] = useState('')

  function handleSubmit(e) {
    e.preventDefault()
    const v = input.trim()
    if (v) setQuery(v)
  }

  return (
    <div className="max-w-2xl mx-auto px-4 py-8 animate-fade-in">
      <h1 className="text-3xl font-bold mb-1 text-white">🌸 皮克敏探索</h1>
      <p className="text-slate-400 mb-6">
        Pikmin Bloom 玩家專用：查詢目的地有哪些特別 / 地區限定皮克敏。
      </p>

      <form onSubmit={handleSubmit} className="flex gap-2 mb-6">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="輸入地點，例如：東京、台南、巴黎"
          className="input flex-1"
        />
        <button type="submit" className="btn-lime">
          查詢
        </button>
      </form>

      {query ? (
        // 以 query 為 key，換地點時重新載入
        <PikminAdvice key={query} location={query} autoLoad />
      ) : (
        <div className="empty">輸入地點開始查詢</div>
      )}
    </div>
  )
}

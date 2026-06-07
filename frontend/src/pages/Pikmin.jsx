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
    <div className="max-w-2xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-1">🌸 皮克敏探索</h1>
      <p className="text-slate-500 mb-6">
        Pikmin Bloom 玩家專用：查詢目的地有哪些特別 / 地區限定皮克敏。
      </p>

      <form onSubmit={handleSubmit} className="flex gap-2 mb-6">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="輸入地點，例如：東京、台南、巴黎"
          className="flex-1 border border-slate-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-lime-500"
        />
        <button
          type="submit"
          className="bg-lime-600 text-white px-5 py-2 rounded-md font-medium hover:bg-lime-700"
        >
          查詢
        </button>
      </form>

      {query ? (
        // 以 query 為 key，換地點時重新載入
        <PikminAdvice key={query} location={query} autoLoad />
      ) : (
        <div className="text-center text-slate-400 py-12 border-2 border-dashed border-slate-200 rounded-xl">
          輸入地點開始查詢
        </div>
      )}
    </div>
  )
}

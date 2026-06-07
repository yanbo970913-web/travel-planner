import { useState } from 'react'

export default function ItineraryForm({ onSubmit, loading }) {
  const [form, setForm] = useState({
    location: '',
    days: 2,
    budget: '',
    preferences: '',
  })

  function update(key, value) {
    setForm((f) => ({ ...f, [key]: value }))
  }

  function handleSubmit(e) {
    e.preventDefault()
    onSubmit({
      location: form.location.trim(),
      days: Number(form.days),
      budget: form.budget.trim() || null,
      preferences: form.preferences.trim() || null,
    })
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 space-y-4"
    >
      <div>
        <label className="block text-sm font-medium mb-1">目的地 *</label>
        <input
          required
          value={form.location}
          onChange={(e) => update('location', e.target.value)}
          placeholder="例如：台南、東京、巴黎"
          className="w-full border border-slate-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-brand-500"
        />
      </div>

      <div>
        <label className="block text-sm font-medium mb-1">天數 *</label>
        <input
          required
          type="number"
          min="1"
          max="30"
          value={form.days}
          onChange={(e) => update('days', e.target.value)}
          className="w-full border border-slate-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-brand-500"
        />
      </div>

      <div>
        <label className="block text-sm font-medium mb-1">預算（選填）</label>
        <input
          value={form.budget}
          onChange={(e) => update('budget', e.target.value)}
          placeholder="例如：每人 1 萬元、小資輕旅行"
          className="w-full border border-slate-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-brand-500"
        />
      </div>

      <div>
        <label className="block text-sm font-medium mb-1">偏好（選填）</label>
        <textarea
          value={form.preferences}
          onChange={(e) => update('preferences', e.target.value)}
          rows={3}
          placeholder="例如：喜歡美食與老街、想避開人潮、帶長輩同行"
          className="w-full border border-slate-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-brand-500"
        />
      </div>

      <button
        type="submit"
        disabled={loading}
        className="w-full bg-brand-600 text-white py-2.5 rounded-md font-medium hover:bg-brand-700 disabled:opacity-60"
      >
        {loading ? 'AI 規劃中…（約需數十秒）' : '產生行程'}
      </button>
    </form>
  )
}

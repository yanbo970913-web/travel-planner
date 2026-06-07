// 將 plan 依 day 分組，以時間軸卡片呈現
export default function ItineraryView({ itinerary }) {
  if (!itinerary) return null

  const byDay = {}
  for (const seg of itinerary.plan) {
    if (!byDay[seg.day]) byDay[seg.day] = []
    byDay[seg.day].push(seg)
  }
  const days = Object.keys(byDay)
    .map(Number)
    .sort((a, b) => a - b)

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold">{itinerary.title}</h2>
        <p className="text-slate-500 text-sm mt-1">
          {itinerary.location} · {itinerary.days} 天
          {itinerary.budget ? ` · 預算：${itinerary.budget}` : ''}
        </p>
        {itinerary.preferences && (
          <p className="text-slate-500 text-sm">偏好：{itinerary.preferences}</p>
        )}
      </div>

      {days.map((day) => (
        <div key={day} className="bg-white rounded-xl border border-slate-200 p-5">
          <h3 className="font-bold text-brand-600 mb-3">第 {day} 天</h3>
          <ol className="relative border-l-2 border-brand-100 ml-2 space-y-4">
            {byDay[day].map((seg, idx) => (
              <li key={idx} className="ml-4">
                <span className="absolute -left-[7px] w-3 h-3 bg-brand-500 rounded-full mt-1.5" />
                <div className="text-sm font-semibold text-brand-700">
                  {seg.time} · {seg.location}
                </div>
                <p className="text-slate-600 text-sm mt-0.5">{seg.description}</p>
              </li>
            ))}
          </ol>
        </div>
      ))}
    </div>
  )
}

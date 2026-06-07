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

  // 依出發日期計算每天日期
  function dayDate(dayNum) {
    if (!itinerary.start_date) return null
    const d = new Date(itinerary.start_date)
    if (isNaN(d)) return null
    d.setDate(d.getDate() + (dayNum - 1))
    return d.toLocaleDateString('zh-TW', { month: 'numeric', day: 'numeric', weekday: 'short' })
  }

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h2 className="text-2xl font-bold text-white">{itinerary.title}</h2>
        <p className="text-slate-400 text-sm mt-1">
          {itinerary.origin ? `${itinerary.origin} → ` : ''}
          {itinerary.location} · {itinerary.days} 天
          {itinerary.start_date ? ` · ${itinerary.start_date} 出發` : ''}
          {itinerary.budget ? ` · 預算：${itinerary.budget}` : ''}
        </p>
        {(itinerary.departure_time || itinerary.return_time) && (
          <p className="text-slate-500 text-xs mt-0.5">
            {itinerary.departure_time ? `去程 ${itinerary.departure_time}` : ''}
            {itinerary.departure_time && itinerary.return_time ? ' · ' : ''}
            {itinerary.return_time ? `回程 ${itinerary.return_time}` : ''}
          </p>
        )}
        {itinerary.preferences && (
          <p className="text-slate-400 text-sm">偏好：{itinerary.preferences}</p>
        )}
      </div>

      {days.map((day) => (
        <div key={day} className="card p-5">
          <h3 className="font-bold text-brand-400 mb-3">
            第 {day} 天{dayDate(day) ? ` · ${dayDate(day)}` : ''}
          </h3>
          <ol className="relative border-l-2 border-slate-700 ml-2 space-y-4">
            {byDay[day].map((seg, idx) => (
              <li key={idx} className="ml-4">
                <span className="absolute -left-[7px] w-3 h-3 bg-brand-500 rounded-full mt-1.5 ring-4 ring-brand-500/20" />
                <div className="text-sm font-semibold text-brand-300">
                  {seg.time} · {seg.location}
                </div>
                <p className="text-slate-300 text-sm mt-0.5">{seg.description}</p>
              </li>
            ))}
          </ol>
        </div>
      ))}
    </div>
  )
}

import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import client, { apiError } from '../api/client'
import ItineraryView from '../components/ItineraryView'
import PikminAdvice from '../components/PikminAdvice'
import WeatherForecast from '../components/WeatherForecast'

export default function ItineraryDetail() {
  const { id } = useParams()
  const [itinerary, setItinerary] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    client
      .get(`/itineraries/${id}`)
      .then((res) => setItinerary(res.data))
      .catch((err) => setError(apiError(err, '找不到此行程')))
      .finally(() => setLoading(false))
  }, [id])

  return (
    <div className="max-w-3xl mx-auto px-4 py-8 animate-fade-in">
      <Link to="/history" className="link text-sm">
        ← 返回歷史行程
      </Link>
      <div className="mt-4">
        {loading ? (
          <div className="flex justify-center py-16">
            <span className="spinner" />
          </div>
        ) : error ? (
          <div className="alert-error">{error}</div>
        ) : (
          <>
            <ItineraryView itinerary={itinerary} />
            {/* 融入行程：目的地天氣預報 */}
            <div className="mt-6">
              <WeatherForecast
                location={itinerary.location}
                startDate={itinerary.start_date}
                days={itinerary.days}
              />
            </div>
            {/* 融入行程：此目的地的皮克敏情報 */}
            <div className="mt-6">
              <PikminAdvice location={itinerary.location} />
            </div>
          </>
        )}
      </div>
    </div>
  )
}

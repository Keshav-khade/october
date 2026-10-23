import React, { useContext, useEffect, useMemo, useState } from 'react'
import axios from 'axios'
import { toast } from 'react-toastify'
import { useNavigate } from 'react-router-dom'
import { AppContext } from '../context/AppContext'

const MIN_SYMPTOMS = 3

// "skin_rash" -> "skin rash" (sirf dikhane ke liye, backend ko original naam jaata hai)
const prettify = (name) => name.replace(/_/g, ' ').replace(/\s+/g, ' ').trim()

const SymptomChecker = () => {

  const { backendUrl } = useContext(AppContext)
  const navigate = useNavigate()

  const [allSymptoms, setAllSymptoms] = useState([])
  const [selected, setSelected] = useState([])
  const [query, setQuery] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)

  // 1. Page khulte hi symptoms ki list lao (ek baar)
  useEffect(() => {
    const loadSymptoms = async () => {
      try {
        const { data } = await axios.get(backendUrl + '/api/user/symptoms')
        if (data.success) {
          setAllSymptoms(data.symptoms)
        } else {
          toast.error(data.message)
        }
      } catch (error) {
        toast.error(error.message)
      }
    }
    loadSymptoms()
  }, [backendUrl])

  // 2. Search box ke hisaab se suggestions (selected wale hata ke, max 8)
  const suggestions = useMemo(() => {
    const q = query.trim().toLowerCase()
    if (!q) return []
    return allSymptoms
      .filter((s) => !selected.includes(s) && prettify(s).toLowerCase().includes(q))
      .slice(0, 8)
  }, [query, allSymptoms, selected])

  const addSymptom = (s) => {
    setSelected((prev) => [...prev, s])
    setQuery('')
    setResult(null)
  }

  const removeSymptom = (s) => {
    setSelected((prev) => prev.filter((x) => x !== s))
    setResult(null)
  }

  // 3. Check button
  const checkSymptoms = async () => {
    if (selected.length < MIN_SYMPTOMS) {
      return toast.error(`Kam se kam ${MIN_SYMPTOMS} symptoms chuniye`)
    }
    setLoading(true)
    try {
      const { data } = await axios.post(backendUrl + '/api/user/predict-doctors', { symptoms: selected })
      if (data.success) {
        setResult(data)
      } else {
        toast.error(data.message)
      }
    } catch (error) {
      toast.error(error.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className='my-16 md:mx-10 flex flex-col items-center gap-4 text-gray-900'>
      <h1 className='text-3xl font-medium text-center'>Not sure which doctor to see?</h1>
      <p className='sm:w-1/2 text-center text-sm text-gray-600'>
        Apne symptoms chuniye, hum suggest karenge ki kis speciality ke doctor se milna chahiye.
      </p>

      <div className='w-full max-w-2xl border border-blue-200 rounded-xl p-5 sm:p-6 bg-white'>

        {/* Search box + suggestions */}
        <div className='relative'>
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className='w-full border rounded px-3 py-2 text-sm'
            type='text'
            placeholder='Symptom likhiye (jaise: headache, itching)'
          />
          {suggestions.length > 0 && (
            <ul className='absolute z-10 w-full bg-white border rounded mt-1 shadow-md max-h-56 overflow-y-auto'>
              {suggestions.map((s) => (
                <li
                  key={s}
                  onClick={() => addSymptom(s)}
                  className='px-3 py-2 text-sm cursor-pointer hover:bg-blue-50'
                >
                  {prettify(s)}
                </li>
              ))}
            </ul>
          )}
        </div>

        {/* Selected chips */}
        <div className='flex flex-wrap gap-2 mt-4 min-h-8'>
          {selected.map((s) => (
            <span key={s} className='flex items-center gap-2 bg-blue-50 border border-blue-200 text-sm px-3 py-1 rounded-full'>
              {prettify(s)}
              <button onClick={() => removeSymptom(s)} className='text-gray-500 hover:text-red-500'>×</button>
            </span>
          ))}
        </div>

        <div className='flex items-center justify-between mt-4 gap-3'>
          <p className='text-xs text-gray-500'>
            {selected.length} chune gaye (kam se kam {MIN_SYMPTOMS} chahiye)
          </p>
          <button
            onClick={checkSymptoms}
            disabled={loading || selected.length < MIN_SYMPTOMS}
            className='bg-primary text-white text-sm px-8 py-2 rounded-full disabled:opacity-50 disabled:cursor-not-allowed'
          >
            {loading ? 'Checking...' : 'Check'}
          </button>
        </div>
      </div>

      {/* Result */}
      {result && (
        <div className='w-full max-w-4xl flex flex-col gap-5 mt-4'>

          {result.prediction.emergency && (
            <div className='border border-red-300 bg-red-50 text-red-700 rounded-lg p-4 text-sm'>
              Aapke chune hue symptoms serious ho sakte hain. Agar takleef zyada hai to apne najdeeki hospital
              ya emergency service se turant sampark karein.
            </div>
          )}

          <div className='border rounded-xl p-5 bg-white'>
            <p className='text-sm text-gray-500'>Suggested speciality</p>
            <p className='text-2xl font-medium text-primary'>{result.prediction.speciality}</p>

            {result.prediction.low_confidence && (
              <p className='text-sm text-amber-600 mt-2'>
                Model in symptoms par pakka nahi hai, isliye General Physician se shuru karna behtar rahega.
                Aur symptoms jodne se result behtar ho sakta hai.
              </p>
            )}

            <p className='text-sm text-gray-500 mt-4 mb-2'>Possible conditions (match score)</p>
            <div className='flex flex-col gap-3'>
              {result.prediction.conditions.map((c) => (
                <div key={c.disease}>
                  <div className='flex justify-between text-sm'>
                    <span>{c.disease}</span>
                    <span className='text-gray-500'>{Math.round(c.score * 100)}%</span>
                  </div>
                  <div className='h-2 bg-gray-100 rounded-full overflow-hidden'>
                    <div className='h-2 bg-primary rounded-full' style={{ width: `${Math.round(c.score * 100)}%` }}></div>
                  </div>
                </div>
              ))}
            </div>

            <p className='text-xs text-gray-500 mt-4'>{result.prediction.disclaimer}</p>
          </div>

          {/* Doctors */}
          <div>
            <p className='text-lg font-medium mb-3'>Available {result.prediction.speciality} doctors</p>
            {result.doctors.length === 0 ? (
              <p className='text-sm text-gray-500'>Abhi is speciality ka koi doctor available nahi hai.</p>
            ) : (
              <div className='w-full grid grid-cols-auto gap-4 gap-y-6'>
                {result.doctors.map((item) => (
                  <div
                    key={item._id}
                    onClick={() => { navigate(`/appointments/${item._id}`); scrollTo(0, 0) }}
                    className='border border-blue-200 rounded-xl overflow-hidden cursor-pointer hover:translate-y-[-10px] transition-all duration-500'
                  >
                    <img className='bg-blue-50' src={item.image} alt='' />
                    <div className='p-4'>
                      <div className='flex items-center gap-2 text-sm text-green-500'>
                        <p className='w-2 h-2 bg-green-500 rounded-full'></p>
                        <p>Available</p>
                      </div>
                      <p className='text-gray-900 text-lg font-medium'>{item.name}</p>
                      <p className='text-gray-600 text-sm'>{item.speciality}</p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

        </div>
      )}
    </div>
  )
}

export default SymptomChecker
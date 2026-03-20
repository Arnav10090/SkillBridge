import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: `${API_URL}/api/v1`,
  timeout: 120000,
})

export const analyzeDocuments = async (resumeFile, jdFile) => {
  const form = new FormData()
  form.append('resume', resumeFile)
  form.append('jd', jdFile)
  const res = await api.post('/analyze', form, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
  return res.data
}

export const pollStatus = async (jobId) => {
  const res = await api.get(`/status/${jobId}`)
  return res.data
}

export const getResults = async (jobId) => {
  const res = await api.get(`/results/${jobId}`)
  return res.data
}

export const getStats = async () => {
  const res = await api.get('/stats')
  return res.data
}

export default api
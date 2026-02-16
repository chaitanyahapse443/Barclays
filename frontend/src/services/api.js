const API_BASE = process.env.REACT_APP_API_BASE || 'http://localhost:8000'

export async function generateSar(caseId){
  const res = await fetch(`${API_BASE}/sars/generate?case_id=${caseId}`, {method: 'POST'})
  return res.json()
}

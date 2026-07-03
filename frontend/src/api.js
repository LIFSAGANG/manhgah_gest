// API Client pour communiquer avec Django
const API_BASE = ''

function getCookie(name) {
  const cookieValue = document.cookie
    .split('; ')
    .find((row) => row.startsWith(`${name}=`))
    ?.split('=')[1]
  return cookieValue ? decodeURIComponent(cookieValue) : ''
}

async function apiCall(url, options = {}) {
  const fullUrl = `${API_BASE}${url}`
  const csrfToken = getCookie('csrftoken')
  const method = options.method || 'GET'
  
  try {
    const response = await fetch(fullUrl, {
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
        ...(method !== 'GET' && { 'X-CSRFToken': csrfToken }),
        ...options.headers,
      },
      ...options,
    })

    if (!response.ok) {
      throw new Error(`API Error: ${response.status}`)
    }

    if (response.status === 204) return null
    return response.json()
  } catch (error) {
    console.error('API Call Error:', error)
    throw error
  }
}

// Produits
export function fetchProduits() {
  return apiCall('/api/produits/')
}

export function addProduit(data) {
  return apiCall('/api/produits/', { method: 'POST', body: JSON.stringify(data) })
}

export function deleteProduit(id) {
  return apiCall(`/api/produits/${id}/`, { method: 'DELETE' })
}

// Catégories
export function fetchCategories() {
  return apiCall('/api/categories/')
}

export function addCategorie(data) {
  return apiCall('/api/categories/', { method: 'POST', body: JSON.stringify(data) })
}

// Sociétés
export function fetchSocietes() {
  return apiCall('/api/societes/')
}

// Agences
export function fetchAgences() {
  return apiCall('/api/agences/')
}

// Mouvements
export function fetchMouvements() {
  return apiCall('/api/mouvements/')
}

export function addMouvement(data) {
  return apiCall('/api/mouvements/', { method: 'POST', body: JSON.stringify(data) })
}

// Generic
export function fetchJson(url) {
  return apiCall(url)
}

export function postJson(url, payload) {
  return apiCall(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': csrfToken,
    },
    body: JSON.stringify(payload),
  })
}

export function deleteJson(url) {
  const csrfToken = getCookie('csrftoken')
  return requestJson(url, {
    method: 'DELETE',
    headers: {
      'X-CSRFToken': csrfToken,
    },
  })
}

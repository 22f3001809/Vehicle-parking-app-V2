import axios from 'axios'
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api'

// Create axios instance
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor for token refresh
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      const refreshToken = localStorage.getItem('refresh_token')
      if (refreshToken) {
        try {
          const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {}, {
            headers: {
              Authorization: `Bearer ${refreshToken}`,
            },
          })

          const { access_token } = response.data
          localStorage.setItem('access_token', access_token)

          // Retry the original request
          originalRequest.headers.Authorization = `Bearer ${access_token}`
          return apiClient(originalRequest)
        } catch (refreshError) {
          // Refresh failed, redirect to login
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          window.location.href = '/login'
          return Promise.reject(refreshError)
        }
      } else {
        // No refresh token, redirect to login
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        window.location.href = '/login'
      }
    }

    return Promise.reject(error)
  }
)

// API Methods
export const api = {
  // Authentication
  auth: {
    login: (credentials) => apiClient.post('/auth/login', credentials),
    register: (userData) => apiClient.post('/auth/register', userData),
    refresh: () => apiClient.post('/auth/refresh'),
    getCurrentUser: () => apiClient.get('/auth/me'),
    logout: () => apiClient.post('/auth/logout'),
  },

  // User endpoints
  user: {
    getDashboard: () => apiClient.get('/user/dashboard'),
    getProfile: () => apiClient.get('/user/profile'),
    updateProfile: (data) => apiClient.put('/user/profile', data),
    changePassword: (data) => apiClient.post('/user/change-password', data),
    getParkingLots: () => apiClient.get('/user/parking-lots'),
    getReservations: (page = 1, perPage = 10) => 
      apiClient.get(`/user/reservations?page=${page}&per_page=${perPage}`),
    bookSpot: (lotId, data) => apiClient.post(`/user/parking-lots/${lotId}/book`, data),
    checkIn: (reservationId) => apiClient.post(`/user/reservations/${reservationId}/checkin`),
    checkOut: (reservationId) => apiClient.post(`/user/reservations/${reservationId}/release`),
    cancelReservation: (reservationId) => apiClient.post(`/user/reservations/${reservationId}/cancel`),
    
    // CSV Export endpoints
    exportCsv: () => apiClient.post('/user/export-csv'),
    getExportStatus: (taskId) => apiClient.get(`/user/export-status/${taskId}`),
  },

  // Admin endpoints
  admin: {
    getDashboard: () => apiClient.get('/admin/dashboard'),
    getDailySummary: () => apiClient.get('/admin/dashboard/daily-summary'),
    getParkingLots: () => apiClient.get('/admin/parking-lots'),
    createParkingLot: (data) => apiClient.post('/admin/parking-lots', data),
    updateParkingLot: (lotId, data) => apiClient.put(`/admin/parking-lots/${lotId}`, data),
    deleteParkingLot: (lotId) => apiClient.delete(`/admin/parking-lots/${lotId}`),
    getLotSpots: (lotId) => apiClient.get(`/admin/parking-lots/${lotId}/spots`),
    getAllUsers: () => apiClient.get('/admin/users'),
    getUserDetails: (userId) => apiClient.get(`/admin/users/${userId}`),
    getAllReservations: (page = 1, perPage = 20) => 
      apiClient.get(`/admin/reservations?page=${page}&per_page=${perPage}`),
  },

  // Public parking endpoints (for viewing lots)
  parking: {
    getPublicLots: () => apiClient.get('/user/parking-lots'),
    getLotDetails: (lotId) => apiClient.get(`/user/parking-lots/${lotId}`),
  },

}

export default apiClient
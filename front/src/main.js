import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import axios from 'axios'
import { api } from './services/api'
import { formatDateTime, formatDate, formatTime, formatRelativeTime, formatDuration, formatCurrency } from './utils/dateTime'

// Import Bootstrap CSS and JS
import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap-icons/font/bootstrap-icons.css'

// Import Font Awesome
import '@fortawesome/fontawesome-free/css/all.css'

// Import Bootstrap JS for interactive components
import 'bootstrap/dist/js/bootstrap.bundle.min.js'

// Import custom styles
import './assets/styles/variables.css'
import './assets/styles/global.css'
import './assets/styles/components.css'

// Configure axios defaults - match the API base URL
// Vite exposes env vars on import.meta.env and only variables prefixed with VITE_
// Keep localhost fallback for dev.
axios.defaults.baseURL =
  import.meta.env.VITE_API_URL || 'http://localhost:5000/api'

// Set up token from localStorage if it exists
const token = localStorage.getItem('access_token')
if (token) {
  axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
}

const app = createApp(App)

// Add HTTP clients to global properties
app.config.globalProperties.$http = axios
app.config.globalProperties.$api = api

// Add date/time formatting utilities as global properties
app.config.globalProperties.$formatDateTime = formatDateTime
app.config.globalProperties.$formatDate = formatDate
app.config.globalProperties.$formatTime = formatTime
app.config.globalProperties.$formatRelativeTime = formatRelativeTime
app.config.globalProperties.$formatDuration = formatDuration
app.config.globalProperties.$formatCurrency = formatCurrency

// Register global filters (Vue 3 way)
app.config.globalProperties.$filters = {
  capitalize: (value) => {
    if (!value) return ''
    value = value.toString()
    return value.charAt(0).toUpperCase() + value.slice(1)
  },
  currency: formatCurrency,
  dateTime: formatDateTime,
  date: formatDate,
  time: formatTime,
  relative: formatRelativeTime
}

app.use(store)
app.use(router)

app.mount('#app')
// Date and time formatting utilities for Indian timezone (IST)

/**
 * Format a date/time string to Indian Standard Time (IST)
 * @param {string|Date} dateString - The date string or Date object to format
 * @param {boolean} includeTime - Whether to include time in the output (default: true)
 * @returns {string} Formatted date string in IST
 */
export function formatDateTime(dateString, includeTime = true) {
  if (!dateString) return 'N/A'
  
  try {
    const date = new Date(dateString)
    
    // Check if date is valid
    if (isNaN(date.getTime())) return 'Invalid Date'
    
    const options = {
      timeZone: 'Asia/Kolkata',
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    }
    
    if (includeTime) {
      options.hour = '2-digit'
      options.minute = '2-digit'
      options.hour12 = true
    }
    
    return new Intl.DateTimeFormat('en-IN', options).format(date)
  } catch (error) {
    console.error('Error formatting date:', error)
    return 'Invalid Date'
  }
}

/**
 * Format date to show only the date part in IST
 * @param {string|Date} dateString - The date string or Date object to format
 * @returns {string} Formatted date string
 */
export function formatDate(dateString) {
  return formatDateTime(dateString, false)
}

/**
 * Format date to show only the time part in IST
 * @param {string|Date} dateString - The date string or Date object to format
 * @returns {string} Formatted time string
 */
export function formatTime(dateString) {
  if (!dateString) return 'N/A'
  
  try {
    const date = new Date(dateString)
    
    if (isNaN(date.getTime())) return 'Invalid Time'
    
    return new Intl.DateTimeFormat('en-IN', {
      timeZone: 'Asia/Kolkata',
      hour: '2-digit',
      minute: '2-digit',
      hour12: true
    }).format(date)
  } catch (error) {
    console.error('Error formatting time:', error)
    return 'Invalid Time'
  }
}

/**
 * Format date to a relative time string (e.g., "2 hours ago")
 * @param {string|Date} dateString - The date string or Date object to format
 * @returns {string} Relative time string
 */
export function formatRelativeTime(dateString) {
  if (!dateString) return 'N/A'
  
  try {
    const date = new Date(dateString)
    const now = new Date()
    
    if (isNaN(date.getTime())) return 'Invalid Date'
    
    const diffMs = now - date
    const diffSecs = Math.floor(diffMs / 1000)
    const diffMins = Math.floor(diffSecs / 60)
    const diffHours = Math.floor(diffMins / 60)
    const diffDays = Math.floor(diffHours / 24)
    
    if (diffSecs < 60) return 'Just now'
    if (diffMins < 60) return `${diffMins} minute${diffMins !== 1 ? 's' : ''} ago`
    if (diffHours < 24) return `${diffHours} hour${diffHours !== 1 ? 's' : ''} ago`
    if (diffDays < 7) return `${diffDays} day${diffDays !== 1 ? 's' : ''} ago`
    
    // For older dates, show the full date
    return formatDateTime(dateString)
  } catch (error) {
    console.error('Error formatting relative time:', error)
    return 'Invalid Date'
  }
}

/**
 * Format duration in hours and minutes
 * @param {number} minutes - Duration in minutes
 * @returns {string} Formatted duration string
 */
export function formatDuration(minutes) {
  if (!minutes || minutes < 0) return '0 min'
  
  const hours = Math.floor(minutes / 60)
  const mins = Math.floor(minutes % 60)
  
  if (hours === 0) return `${mins} min${mins !== 1 ? 's' : ''}`
  if (mins === 0) return `${hours} hour${hours !== 1 ? 's' : ''}`
  
  return `${hours} hour${hours !== 1 ? 's' : ''} ${mins} min${mins !== 1 ? 's' : ''}`
}

/**
 * Format currency in Indian Rupees
 * @param {number} amount - The amount to format
 * @returns {string} Formatted currency string
 */
export function formatCurrency(amount) {
  if (amount === null || amount === undefined) return '₹0'
  
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    minimumFractionDigits: 0,
    maximumFractionDigits: 2
  }).format(amount)
}

/**
 * Get current date/time in IST
 * @returns {Date} Current date in IST
 */
export function getCurrentISTTime() {
  return new Date(new Date().toLocaleString('en-US', { timeZone: 'Asia/Kolkata' }))
}

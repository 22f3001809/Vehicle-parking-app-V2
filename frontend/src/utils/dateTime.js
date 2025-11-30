// Date and time formatting utilities for Indian timezone (IST)

export function formatDateTime(dateString, includeTime = true) {
  if (!dateString) return 'N/A'
  
  try {
    const date = new Date(dateString)
    
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

export function formatDate(dateString) {
  return formatDateTime(dateString, false)
}

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
    
    return formatDateTime(dateString)
  } catch (error) {
    console.error('Error formatting relative time:', error)
    return 'Invalid Date'
  }
}

export function formatDuration(minutes) {
  if (!minutes || minutes < 0) return '0 min'
  
  const hours = Math.floor(minutes / 60)
  const mins = Math.floor(minutes % 60)
  
  if (hours === 0) return `${mins} min${mins !== 1 ? 's' : ''}`
  if (mins === 0) return `${hours} hour${hours !== 1 ? 's' : ''}`
  
  return `${hours} hour${hours !== 1 ? 's' : ''} ${mins} min${mins !== 1 ? 's' : ''}`
}

export function formatCurrency(amount) {
  if (amount === null || amount === undefined) return '₹0'
  
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    minimumFractionDigits: 0,
    maximumFractionDigits: 2
  }).format(amount)
}

export function getCurrentISTTime() {
  return new Date(new Date().toLocaleString('en-US', { timeZone: 'Asia/Kolkata' }))
}

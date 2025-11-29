<template>
  <div class="container-fluid py-4">
    <!-- Dashboard Header -->
    <div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom">
      <h1 class="h2 text-primary">Welcome, {{ user?.full_name }}!</h1>
    </div>

    <!-- Current Active Reservation -->
    <div v-if="activeReservation" class="card mb-4 shadow-sm">
      <div class="card-header bg-primary text-white">
        <h5 class="my-0 font-weight-normal">Your Current Reservation</h5>
      </div>
      <div class="card-body">
        <div class="row">
          <div class="col-md-6">
            <p><strong>Reservation ID:</strong> {{ activeReservation.id }}</p>
            <p><strong>Parking Lot:</strong> {{ activeReservation.lot_name || 'N/A' }}</p>
            <p><strong>Spot Number:</strong> {{ activeReservation.spot_number || 'N/A' }}</p>
            <p><strong>Vehicle Number:</strong> {{ activeReservation.vehicle_number }}</p>
          </div>
          <div class="col-md-6">
            <p><strong>Booked At:</strong> {{ formatDateTime(activeReservation.booking_timestamp) }}</p>
            <p v-if="activeReservation.check_in_timestamp"><strong>Check-in Time:</strong> {{ formatDateTime(activeReservation.check_in_timestamp) }}</p>
            <p><strong>Status: </strong> 
              <span :class="getStatusBadgeClass(activeReservation.status)" class="badge">
                {{ activeReservation.status }}
              </span>
            </p>
          </div>
        </div>
        <div class="mt-3">
          <button 
            v-if="activeReservation.status === 'pending'" 
            @click="checkIn(activeReservation.id)"
            class="btn btn-success me-2"
            :disabled="processing"
          >
            {{ processing ? 'Processing...' : 'Check In Now' }}
          </button>
          <button 
            v-if="activeReservation.status === 'pending'" 
            @click="cancelReservation(activeReservation.id)"
            class="btn btn-danger"
            :disabled="processing"
          >
            {{ processing ? 'Processing...' : 'Cancel Reservation' }}
          </button>
          <button 
            v-if="activeReservation.status === 'active'" 
            @click="checkOut(activeReservation.id)"
            class="btn btn-primary"
            :disabled="processing"
          >
            {{ processing ? 'Processing...' : 'Check Out' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Quick Stats -->
    <div class="row mb-4">
      <div class="col-md-3 mb-3">
        <div class="card text-center h-100 shadow-sm">
          <div class="card-body">
            <div class="text-primary mb-2">
              <i class="fas fa-car fa-2x"></i>
            </div>
            <h4 class="card-title text-primary">{{ userStats.active_reservations || 0 }}</h4>
            <p class="card-text text-muted">Active Reservations</p>
          </div>
        </div>
      </div>
      <div class="col-md-3 mb-3">
        <div class="card text-center h-100 shadow-sm">
          <div class="card-body">
            <div class="text-success mb-2">
              <i class="fas fa-calendar-check fa-2x"></i>
            </div>
            <h4 class="card-title text-success">{{ userStats.total_reservations || 0 }}</h4>
            <p class="card-text text-muted">Total Bookings</p>
          </div>
        </div>
      </div>
      <div class="col-md-3 mb-3">
        <div class="card text-center h-100 shadow-sm">
          <div class="card-body">
            <div class="text-warning mb-2">
              <i class="fas fa-rupee-sign fa-2x"></i>
            </div>
            <h4 class="card-title text-warning">₹{{ userStats.total_spent || 0 }}</h4>
            <p class="card-text text-muted">Total Spent</p>
          </div>
        </div>
      </div>
      <div class="col-md-3 mb-3">
        <div class="card text-center h-100 shadow-sm">
          <div class="card-body">
            <div class="text-info mb-2">
              <i class="fas fa-calendar fa-2x"></i>
            </div>
            <h4 class="card-title text-info">{{ userStats.completed_reservations || 0 }}</h4>
            <p class="card-text text-muted">Completed</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Search Parking Lots -->
    <div class="card mb-4 shadow-sm">
      <div class="card-header">
        <h5 class="mb-0">
          <i class="fas fa-search me-2"></i>
          Find Parking
        </h5>
      </div>
      <div class="card-body">
        <form @submit.prevent="searchParkingLots" class="d-flex mb-3">
          <input 
            v-model="searchTerm" 
            class="form-control me-2" 
            type="search" 
            placeholder="Search by lot name, address, or location" 
            aria-label="Search"
          >
          <button class="btn btn-outline-primary" type="submit">Search</button>
        </form>
        <div v-if="searchResults.length > 0" class="parking-lots-scroll">
          <div class="row row-cols-1 row-cols-md-2 row-cols-lg-3 g-3">
            <div v-for="lot in searchResults" :key="lot.id" class="col">
              <div class="card h-100 shadow-sm">
                <div class="card-body d-flex flex-column">
                  <h5 class="card-title">{{ lot.name }}</h5>
                  <p class="card-text text-muted">{{ lot.address }}</p>
                  <p class="card-text">Price: ₹{{ lot.price_per_hour }} / hour</p>
                  <p class="card-text">
                    Available Spots: 
                    <span class="badge bg-success">{{ lot.available_spots }} / {{ lot.number_of_spots }}</span>
                  </p>
                  <div class="mt-auto">
                    <router-link 
                      v-if="lot.available_spots > 0" 
                      :to="`/user/book-parking/${lot.id}`" 
                      class="btn btn-primary btn-sm"
                    >
                      Book Spot
                    </router-link>
                    <button v-else class="btn btn-secondary btn-sm" disabled>
                      No Spots Available
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div v-else-if="!loading && searchTerm" class="text-center text-muted py-4">
          <i class="fas fa-search fa-3x mb-3"></i>
          <p>No parking lots found matching your search.</p>
        </div>
      </div>
    </div>

    <!-- Reservation History -->
    <div class="card mb-4 shadow-sm">
      <div class="card-header d-flex justify-content-between align-items-center">
        <h5 class="mb-0">
          <i class="fas fa-history me-2"></i>
          Your Reservation History
        </h5>
        <router-link to="/user/reservations" class="btn btn-sm btn-outline-primary">
          View All
        </router-link>
      </div>
      <div class="card-body">
        <div v-if="loading" class="text-center py-3">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
        </div>
        <div v-else class="table-responsive">
          <table class="table table-striped table-hover">
            <thead>
              <tr>
                <th>ID</th>
                <th>Lot Name</th>
                <th>Spot Number</th>
                <th>Vehicle</th>
                <th>Booked At</th>
                <th>Check-in At</th>
                <th>Left At</th>
                <th>Status</th>
                <th>Cost</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="reservation in recentReservations" :key="reservation.id">
                <td>{{ reservation.id }}</td>
                <td>{{ reservation.lot_name || 'N/A' }}</td>
                <td>{{ reservation.spot_number || 'N/A' }}</td>
                <td>{{ reservation.vehicle_number }}</td>
                <td>{{ formatDateTime(reservation.booking_timestamp) }}</td>
                <td>
                  <span v-if="reservation.check_in_timestamp">
                    {{ formatDateTime(reservation.check_in_timestamp) }}
                  </span>
                  <span v-else class="text-muted">Not checked in</span>
                </td>
                <td>
                  <span v-if="reservation.check_out_timestamp">
                    {{ formatDateTime(reservation.check_out_timestamp) }}
                  </span>
                  <span v-else class="text-muted">-</span>
                </td>
                <td>
                  <span :class="getStatusBadgeClass(reservation.status)" class="badge">
                    {{ reservation.status }}
                  </span>
                </td>
                <td>
                  <span v-if="reservation.parking_cost">
                    ₹{{ reservation.parking_cost }}
                  </span>
                  <span v-else class="text-muted">-</span>
                </td>
                <td class="text-nowrap">
                  <button 
                    v-if="reservation.status === 'pending'" 
                    @click="checkIn(reservation.id)"
                    class="btn btn-sm btn-success me-1"
                    :disabled="processing"
                  >
                    Check In
                  </button>
                  <button 
                    v-if="reservation.status === 'pending'" 
                    @click="cancelReservation(reservation.id)"
                    class="btn btn-sm btn-danger"
                    :disabled="processing"
                  >
                    Cancel
                  </button>
                  <button 
                    v-if="reservation.status === 'active'" 
                    @click="checkOut(reservation.id)"
                    class="btn btn-sm btn-primary btn-sm px-1 me-1"
                    :disabled="processing"
                  >
                    Check Out
                  </button>
                  <span v-if="reservation.status === 'completed' || reservation.status === 'cancelled'" class="text-muted">
                    No Actions
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Export Reservations -->
    <div class="card mb-4 shadow-sm border-info">
  <div class="card-header bg-info text-white">
    <h5 class="mb-0">
      <i class="fas fa-download me-2"></i>
      Export Your Data
    </h5>
  </div>
  <div class="card-body">
    <p class="text-muted mb-3">Download a CSV file of all your parking reservations and history.</p>
    
    <div v-if="exportCompleted" class="alert alert-success">
      <i class="fas fa-check-circle me-2"></i>
      <strong>Export Completed!</strong> Check your email for the CSV file with all your parking history.
      <button 
        @click="resetExport"
        class="btn btn-outline-success btn-sm ms-2"
      >
        Export Again
      </button>
    </div>

    <div v-else-if="exportError" class="alert alert-danger">
      <i class="fas fa-exclamation-circle me-2"></i>
      <strong>Export Failed:</strong> {{ exportError }}
      <button 
        @click="resetExport"
        class="btn btn-outline-danger btn-sm ms-2"
      >
        Try Again
      </button>
    </div>

    <div v-else-if="exportInProgress || exportTaskId">
      <div class="alert alert-info mb-3">
        <i class="fas fa-spinner fa-spin me-2"></i>
        {{ exportStatusMessage }}
      </div>
      
      <div class="progress mb-3" v-if="exportProgress !== null">
        <div 
          class="progress-bar progress-bar-striped progress-bar-animated" 
          role="progressbar"
          :style="{ width: exportProgress + '%' }"
          :aria-valuenow="exportProgress"
          aria-valuemin="0"
          aria-valuemax="100"
        >
          {{ exportProgress }}%
        </div>
      </div>

      <button 
        @click="cancelExport"
        class="btn btn-outline-secondary btn-sm"
      >
        <i class="fas fa-times me-1"></i>
        Cancel Export
      </button>
    </div>

    <div v-else>
      <button 
        @click="triggerCsvExport"
        class="btn btn-info"
        :disabled="processing"
      >
        <i class="fas fa-download me-2"></i>
        {{ processing ? 'Processing...' : 'Export as CSV' }}
      </button>
      <p class="mt-2 text-muted small">
        <i class="fas fa-info-circle"></i>
        The CSV file will be sent to your email.
      </p>
    </div>

  </div>
</div>

    <!-- Account Info -->
    <div class="card shadow-sm">
      <div class="card-header">
        <h5 class="mb-0">
          <i class="fas fa-user me-2"></i>
          Account Information
        </h5>
      </div>
      <div class="card-body">
        <div class="row">
          <div class="col-md-6">
            <p class="mb-2"><strong>Username:</strong> {{ user?.username || 'N/A' }}</p>
            <p class="mb-2"><strong>Full Name:</strong> {{ user?.full_name || 'N/A' }}</p>
            <p class="mb-2"><strong>Email:</strong> {{ user?.email || 'N/A' }}</p>
          </div>
          <div class="col-md-6">
            <p class="mb-2"><strong>Member Since:</strong> {{ user?.created_at ? formatDate(user.created_at) : 'N/A' }}</p>
            <div class="mt-3">
              <router-link to="/profile" class="btn btn-outline-primary me-2">
                <i class="fas fa-user-cog me-1"></i>
                Edit Profile
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapState, mapActions } from 'vuex'

export default {
  name: 'UserDashboard',
  filters: {
    capitalize(value) {
      if (!value) return ''
      value = value.toString()
      return value.charAt(0).toUpperCase() + value.slice(1)
    }
  },
  data() {
    return {
      loading: true,
      processing: false,
      searchTerm: '',
      searchResults: [],
      userReservations: [],
      userStats: {
        active_reservations: 0,
        total_reservations: 0,
        total_spent: 0,
        completed_reservations: 0
      },
      // CSV Export state
      exportTaskId: null,
      exportInProgress: false,
      exportCompleted: false,
      exportError: null,
      exportProgress: null,
      exportStatusMessage: 'Starting CSV export...',
      exportCheckInterval: null
    }
  },
  computed: {
    user() {
      return this.$store.getters.user
    },
    activeReservation() {
      return this.userReservations.find(r => r.status === 'pending' || r.status === 'active')
    },
    recentReservations() {
      return this.userReservations.slice(0, 10)
    }
  },
  methods: {
    ...mapActions('auth', ['fetchCurrentUser']),
    
    async loadDashboardData() {
      this.loading = true
      try {
        // Load reservations and stats
        const [reservationsRes, statsRes] = await Promise.all([
          this.$api.user.getReservations(),
          this.$api.user.getDashboard()
        ])
        
        this.userReservations = Array.isArray(reservationsRes.data) ? reservationsRes.data : []
        this.userStats = statsRes.data || this.userStats
      } catch (error) {
        console.error('Error loading dashboard data:', error)
        this.$store.dispatch('setAlert', {
          message: 'Failed to load dashboard data',
          type: 'error'
        })
      } finally {
        this.loading = false
      }
    },
    
    async searchParkingLots() {
      if (!this.searchTerm.trim()) {
        try {
          const response = await this.$api.parking.getPublicLots()
          this.searchResults = response.data.parking_lots || response.data || []
        } catch (error) {
          console.error('Error loading parking lots:', error)
        }
        return
      }
      
      try {
        const response = await this.$api.parking.getPublicLots()
        const lots = response.data.parking_lots || response.data || []
        
        // Client-side filtering (you can implement server-side search later)
        this.searchResults = lots.filter(lot => 
          lot.name.toLowerCase().includes(this.searchTerm.toLowerCase()) ||
          lot.address.toLowerCase().includes(this.searchTerm.toLowerCase()) ||
          lot.pin_code.includes(this.searchTerm)
        )
      } catch (error) {
        console.error('Error searching parking lots:', error)
        this.$store.dispatch('setAlert', {
          message: 'Failed to search parking lots',
          type: 'error'
        })
      }
    },
    
    async checkIn(reservationId) {
      if (!confirm('Are you sure you want to check in to this parking spot? Parking charges will start from now.')) return
      
      this.processing = true
      try {
        await this.$api.user.checkIn(reservationId)
        this.$store.dispatch('setAlert', {
          message: 'Checked in successfully! Parking cost will be calculated from now.',
          type: 'success'
        })
        // Reload data
        await this.loadDashboardData()
      } catch (error) {
        console.error('Error checking in:', error)
        this.$store.dispatch('setAlert', {
          message: error.response?.data?.error || 'Failed to check in',
          type: 'error'
        })
      } finally {
        this.processing = false
      }
    },
    
    async checkOut(reservationId) {
      if (!confirm('Are you sure you want to check out? Your parking cost will be calculated based on duration.')) return
      
      this.processing = true
      try {
        const response = await this.$api.user.checkOut(reservationId)
        const cost = response.data.cost || response.data.reservation?.parking_cost || 0
        this.$store.dispatch('setAlert', {
          message: `Checked out successfully! Your parking cost is ₹${cost}. Please proceed to payment.`,
          type: 'success'
        })
        // Reload data
        await this.loadDashboardData()
      } catch (error) {
        console.error('Error checking out:', error)
        this.$store.dispatch('setAlert', {
          message: error.response?.data?.error || 'Failed to check out',
          type: 'error'
        })
      } finally {
        this.processing = false
      }
    },
    
    async cancelReservation(reservationId) {
      if (!confirm('Are you sure you want to cancel this reservation?')) return
      
      this.processing = true
      try {
        await this.$api.user.cancelReservation(reservationId)
        this.$store.dispatch('setAlert', {
          message: 'Reservation cancelled successfully',
          type: 'success'
        })
        // Reload data
        await this.loadDashboardData()
      } catch (error) {
        console.error('Error cancelling reservation:', error)
        this.$store.dispatch('setAlert', {
          message: error.response?.data?.error || 'Failed to cancel reservation',
          type: 'error'
        })
      } finally {
        this.processing = false
      }
    },
    
    formatDate(dateString) {
      return this.$formatDate(dateString)
    },
    
    formatDateTime(dateString) {
      return this.$formatDateTime(dateString)
    },
    
    getStatusBadgeClass(status) {
      const classes = {
        'pending': 'bg-warning text-dark',
        'active': 'bg-success',
        'completed': 'bg-info',
        'cancelled': 'bg-danger'
      }
      return classes[status] || 'bg-secondary'
    },
    
    // ─────────────────────────────────────────────────────────────
    // CSV EXPORT METHODS
    // ─────────────────────────────────────────────────────────────
    
    async triggerCsvExport() {
      this.exportInProgress = true
      this.exportError = null
      this.exportCompleted = false
      this.exportProgress = null
      
      try {
        // Trigger the export task
        const response = await this.$api.user.exportCsv()
        
        if (response.status === 202) {
          // Task accepted and started
          this.exportTaskId = response.data.task_id
          this.exportStatusMessage = response.data.message || 'Export started, checking status...'
          
          // Start polling for status
          this.startExportStatusCheck()
        } else {
          throw new Error('Unexpected response from export endpoint')
        }
      } catch (error) {
        console.error('Error triggering CSV export:', error)
        this.exportError = error.response?.data?.error || error.message || 'Failed to start export'
        this.exportInProgress = false
        this.$store.dispatch('setAlert', {
          message: `Export failed: ${this.exportError}`,
          type: 'error'
        })
      }
    },
    
    startExportStatusCheck() {
      // Check status every 2 seconds
      this.exportCheckInterval = setInterval(() => {
        this.checkExportStatus()
      }, 2000)
    },
    
    async checkExportStatus() {
      if (!this.exportTaskId) {
        clearInterval(this.exportCheckInterval)
        return
      }
      
      try {
        const response = await this.$api.user.getExportStatus(this.exportTaskId)
        const status = response.data.status
        
        this.exportStatusMessage = response.data.message || `Export ${status}...`
        
        if (response.data.progress !== undefined) {
          this.exportProgress = response.data.progress
        }
        
        if (status === 'success') {
          // Export completed successfully
          clearInterval(this.exportCheckInterval)
          this.exportCompleted = true
          this.exportInProgress = false
          
          this.$store.dispatch('setAlert', {
            message: 'CSV export completed! Check your email for the file.',
            type: 'success'
          })
        } else if (status === 'error') {
          // Export failed
          clearInterval(this.exportCheckInterval)
          this.exportError = response.data.error || 'Export failed for unknown reason'
          this.exportInProgress = false
          
          this.$store.dispatch('setAlert', {
            message: `Export error: ${this.exportError}`,
            type: 'error'
          })
        }
        // If pending or processing, continue polling
      } catch (error) {
        console.error('Error checking export status:', error)
        // Continue polling even if there's an error (task might still be processing)
      }
    },
    
    cancelExport() {
      if (this.exportCheckInterval) {
        clearInterval(this.exportCheckInterval)
      }
      this.resetExport()
      
      this.$store.dispatch('setAlert', {
        message: 'Export cancelled',
        type: 'info'
      })
    },
    
    resetExport() {
      if (this.exportCheckInterval) {
        clearInterval(this.exportCheckInterval)
      }
      this.exportTaskId = null
      this.exportInProgress = false
      this.exportCompleted = false
      this.exportError = null
      this.exportProgress = null
      this.exportStatusMessage = 'Starting CSV export...'
    }
  },
  
  async mounted() {
    // Ensure user is loaded
    if (!this.user) {
      try {
        await this.fetchCurrentUser()
      } catch (error) {
        console.error('Failed to fetch current user:', error)
        // Redirect to login if user fetch fails
        this.$router.push('/login')
        return
      }
    }
    
    await this.loadDashboardData()
    
    // Load initial parking lots
    await this.searchParkingLots()
  }
}
</script>

<style scoped>
.card {
  border: 1px solid #e3e6f0;
}

.table th {
  border-top: none;
  font-weight: 600;
}

.btn {
  transition: all 0.2s;
}

.btn:hover {
  transform: translateY(-1px);
}

.opacity-75 {
  opacity: 0.75;
}

.parking-lots-scroll {
  max-height: 600px;
  overflow-y: auto;
  border: 1px solid #e3e6f0;
  border-radius: 0.375rem;
  padding: 1rem;
  background-color: #fafbfc;
}

.parking-lots-scroll::-webkit-scrollbar {
  width: 8px;
}

.parking-lots-scroll::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 10px;
}

.parking-lots-scroll::-webkit-scrollbar-thumb {
  background: #0d6efd;
  border-radius: 10px;
}

.parking-lots-scroll::-webkit-scrollbar-thumb:hover {
  background: #0b5ed7;
}
</style>
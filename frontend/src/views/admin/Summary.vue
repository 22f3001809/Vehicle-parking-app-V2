<template>
  <div class="container-fluid py-4">
    <!-- Header -->
    <div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-2 pb-2 border-bottom">
      <h1 class="h2 text-primary">Parking Summary & Analytics</h1>
      <button @click="refreshData" class="btn btn-sm btn-outline-primary" :disabled="loading">
        <i class="fas fa-sync-alt me-1" :class="{ 'fa-spin': loading }"></i>
        Refresh
      </button>
    </div>

    <!-- Quick Stats Cards -->
    <div class="row mt-4 mb-4">
      <div class="col-lg-2 col-md-4 col-sm-6 mb-3">
        <div class="card bg-white text-dark shadow-sm h-100">
          <div class="card-body d-flex flex-column justify-content-between">
            <h6 class="card-title mb-0 text-primary" style="font-size: 0.85rem;">Total Lots</h6>
            <p class="card-text fs-4 text-dark text-end mt-2">{{ stats.totalLots || 0 }}</p>
          </div>
        </div>
      </div>

      <div class="col-lg-2 col-md-4 col-sm-6 mb-3">
        <div class="card bg-white text-dark shadow-sm h-100">
          <div class="card-body d-flex flex-column justify-content-between">
            <h6 class="card-title mb-0 text-success" style="font-size: 0.85rem;">Available</h6>
            <p class="card-text fs-4 text-dark text-end mt-2">{{ stats.availableSpots || 0 }}</p>
          </div>
        </div>
      </div>

      <div class="col-lg-2 col-md-4 col-sm-6 mb-3">
        <div class="card bg-white text-dark shadow-sm h-100">
          <div class="card-body d-flex flex-column justify-content-between">
            <h6 class="card-title mb-0 text-danger" style="font-size: 0.85rem;">Occupied</h6>
            <p class="card-text fs-4 text-dark text-end mt-2">{{ stats.occupiedSpots || 0 }}</p>
          </div>
        </div>
      </div>

      <div class="col-lg-2 col-md-4 col-sm-6 mb-3">
        <div class="card bg-white text-dark shadow-sm h-100">
          <div class="card-body d-flex flex-column justify-content-between">
            <h6 class="card-title mb-0 text-warning" style="font-size: 0.85rem;">Reserved</h6>
            <p class="card-text fs-4 text-dark text-end mt-2">{{ stats.reservedSpots || 0 }}</p>
          </div>
        </div>
      </div>

      <div class="col-lg-2 col-md-4 col-sm-6 mb-3">
        <div class="card bg-white text-dark shadow-sm h-100">
          <div class="card-body d-flex flex-column justify-content-between">
            <h6 class="card-title mb-0 text-info" style="font-size: 0.85rem;">Users</h6>
            <p class="card-text fs-4 text-dark text-end mt-2">{{ stats.totalUsers || 0 }}</p>
          </div>
        </div>
      </div>

      <div class="col-lg-2 col-md-4 col-sm-6 mb-3">
        <div class="card bg-white text-dark shadow-sm h-100">
          <div class="card-body d-flex flex-column justify-content-between">
            <h6 class="card-title mb-0 text-success" style="font-size: 0.85rem;">Revenue</h6>
            <p class="card-text fs-5 text-dark text-end mt-2">₹{{ stats.totalRevenue || 0 }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Charts Section (V1 Style) -->
    <h2 class="mt-4 text-primary">Overview Charts</h2>
    <div class="row mb-4">
      <div v-if="loading" class="col-12 text-center py-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
      </div>
      <template v-else>
        <!-- Daily Revenue Chart (Last 7 Days) -->
        <div class="col-lg-6 col-md-12 mb-3">
          <div class="card shadow-sm h-100">
            <div class="card-header bg-primary text-white">
              <h5 class="mb-0">Daily Revenue (Last 7 Days)</h5>
            </div>
            <div class="card-body" style="height: 300px; position: relative;">
              <canvas id="dailyRevenueChart"></canvas>
            </div>
          </div>
        </div>

        <!-- Daily Bookings Chart (Last 7 Days) -->
        <div class="col-lg-6 col-md-12 mb-3">
          <div class="card shadow-sm h-100">
            <div class="card-header bg-primary text-white">
              <h5 class="mb-0">Daily Bookings (Last 7 Days)</h5>
            </div>
            <div class="card-body" style="height: 300px; position: relative;">
              <canvas id="dailyBookingsChart"></canvas>
            </div>
          </div>
        </div>

        <!-- Parking Spot Status -->
        <div class="col-lg-4 col-md-6 mb-3">
          <div class="card shadow-sm h-100">
            <div class="card-header bg-primary text-white">
              <h5 class="mb-0">Parking Spot Status</h5>
            </div>
            <div class="card-body" style="height: 300px; position: relative;">
              <canvas id="spotStatusChart"></canvas>
            </div>
          </div>
        </div>

        <!-- Reservation Status Breakdown -->
        <div class="col-lg-4 col-md-6 mb-3">
          <div class="card shadow-sm h-100">
            <div class="card-header bg-primary text-white">
              <h5 class="mb-0">Reservation Status Breakdown</h5>
            </div>
            <div class="card-body" style="height: 300px; position: relative;">
              <canvas id="reservationStatusChart"></canvas>
            </div>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script>
import { mapActions } from 'vuex'
import Chart from 'chart.js/auto'

export default {
  name: 'AdminSummary',
  data() {
    return {
      loading: true,
      stats: {
        totalLots: 0,
        totalSpots: 0,
        availableSpots: 0,
        occupiedSpots: 0,
        reservedSpots: 0,
        totalUsers: 0,
        totalRevenue: 0
      },
      recentLots: [],
      charts: {}
    }
  },

  methods: {
    ...mapActions(['setAlert']),

    async loadStats() {
      try {
        this.loading = true

        const response = await this.$api.admin.getDashboard()
        const data = response.data

        this.stats = {
          totalLots: data.total_lots || 0,
          totalSpots: data.total_spots || 0,
          availableSpots: data.available_spots || 0,
          occupiedSpots: data.occupied_spots || 0,
          reservedSpots: data.reserved_spots || 0,
          totalUsers: data.total_users || 0,
          totalRevenue: data.total_revenue || 0
        }

        this.recentLots = data.recent_lots || []

        // Fetch daily summary data for charts
        try {
          const summaryRes = await this.$api.admin.getDailySummary()
          const summaryData = summaryRes.data
          console.log('Daily summary data received:', summaryData)
          
          // Initialize charts with real data - wait a bit for DOM to be ready
          this.$nextTick(async () => {
            await new Promise(resolve => setTimeout(resolve, 100))
            this.initCharts(summaryData)
          })
        } catch (error) {
          console.error('Error loading daily summary:', error)
          // Initialize charts with empty data
          this.$nextTick(async () => {
            await new Promise(resolve => setTimeout(resolve, 100))
            this.initCharts({ daily_data: [], reservation_status: {} })
          })
        }
      } catch (error) {
        console.error('Error loading stats:', error)
        this.setAlert({
          message: 'Failed to load summary data',
          type: 'error'
        })
      } finally {
        this.loading = false
      }
    },

    initCharts(summaryData) {
      console.log('initCharts called with data:', summaryData)
      
      // Destroy existing charts
      Object.values(this.charts).forEach(chart => {
        if (chart) chart.destroy()
      })
      this.charts = {}

      // Extract daily data from real backend response
      const dailyData = summaryData.daily_data || []
      const last7Days = dailyData.length > 0 ? dailyData.map(d => d.date) : this.getLast7Days()
      
      let dailyRevenueAmounts = dailyData.map(d => d.revenue || 0)
      let dailyBookingsCounts = dailyData.map(d => d.bookings || 0)
      
      console.log('Chart data prepared:', { last7Days, dailyRevenueAmounts, dailyBookingsCounts })

      // 1. Daily Revenue Chart (Line - Last 7 Days)
      const dailyRevenueCtx = document.getElementById('dailyRevenueChart')
      console.log('dailyRevenueCtx element:', dailyRevenueCtx)
      if (dailyRevenueCtx) {
        try {
          this.charts.dailyRevenue = new Chart(dailyRevenueCtx, {
          type: 'line',
          data: {
            labels: last7Days,
            datasets: [{
              label: 'Revenue (₹)',
              data: dailyRevenueAmounts,
              borderColor: 'hsl(280, 70%, 55%)',
              backgroundColor: 'hsla(280, 70%, 55%, 0.2)',
              borderWidth: 2,
              fill: true,
              tension: 0.3
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: { display: true, position: 'top', labels: { color: 'var(--bs-dark)' } },
              tooltip: {
                callbacks: {
                  label: function(context) {
                    return context.dataset.label + ': ₹' + context.parsed.y.toFixed(2)
                  }
                }
              }
            },
            scales: {
              y: {
                beginAtZero: true,
                ticks: {
                  callback: function(value) {
                    if (Number.isInteger(value)) {
                      return '₹' + value
                    } else {
                      return '₹' + value.toFixed(2)
                    }
                  },
                  color: 'var(--bs-dark)'
                },
                title: { display: true, text: 'Revenue (₹)', color: 'var(--bs-dark)' },
                grid: { color: 'rgba(0,0,0,0.1)' }
              },
              x: {
                ticks: { color: 'var(--bs-dark)' },
                title: { display: true, text: 'Date', color: 'var(--bs-dark)' },
                grid: { color: 'rgba(0,0,0,0.1)' }
              }
            }
          }
        })
        console.log('Daily Revenue chart created')
      } catch (err) {
        console.error('Error creating Daily Revenue chart:', err)
      }
      }

      // 2. Daily Bookings Chart (Line - Last 7 Days)
      const dailyBookingsCtx = document.getElementById('dailyBookingsChart')
      if (dailyBookingsCtx) {
        try {
          this.charts.dailyBookings = new Chart(dailyBookingsCtx, {
          type: 'line',
          data: {
            labels: last7Days,
            datasets: [{
              label: 'Bookings',
              data: dailyBookingsCounts,
              backgroundColor: 'hsla(210, 70%, 45%, 0.2)',
              borderColor: 'hsl(210, 70%, 45%)',
              borderWidth: 2,
              fill: true,
              tension: 0.3
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: { display: true, position: 'top', labels: { color: 'var(--bs-dark)' } },
              tooltip: {
                callbacks: {
                  label: function(context) {
                    return context.dataset.label + ': ' + context.parsed.y
                  }
                }
              }
            },
            scales: {
              y: {
                beginAtZero: true,
                ticks: {
                  callback: function(value) {
                    if (Number.isInteger(value)) return value
                  },
                  color: 'var(--bs-dark)'
                },
                title: { display: true, text: 'Number of Bookings', color: 'var(--bs-dark)' },
                grid: { color: 'rgba(0,0,0,0.1)' }
              },
              x: {
                ticks: { color: 'var(--bs-dark)' },
                title: { display: true, text: 'Date', color: 'var(--bs-dark)' },
                grid: { color: 'rgba(0,0,0,0.1)' }
              }
            }
          }
        })
        console.log('Daily Bookings chart created')
      } catch (err) {
        console.error('Error creating Daily Bookings chart:', err)
      }
      }

      // 3. Parking Spot Status (Doughnut)
      const spotStatusCtx = document.getElementById('spotStatusChart')
      if (spotStatusCtx) {
        try {
          const hasData = this.stats.availableSpots > 0 || this.stats.occupiedSpots > 0 || this.stats.reservedSpots > 0
          if (hasData) {
            this.charts.spotStatus = new Chart(spotStatusCtx, {
            type: 'doughnut',
            data: {
              labels: ['Available', 'Occupied', 'Reserved'],
              datasets: [{
                data: [this.stats.availableSpots, this.stats.occupiedSpots, this.stats.reservedSpots || 0],
                backgroundColor: [
                  'hsl(140, 60%, 40%)',  // Green - Available
                  'hsl(0, 70%, 50%)',     // Red - Occupied
                  'hsl(200, 70%, 45%)'    // Blue - Reserved
                ],
                borderColor: '#fff',
                borderWidth: 1
              }]
            },
            options: {
              responsive: true,
              maintainAspectRatio: false,
              plugins: {
                legend: { position: 'top', labels: { color: 'var(--bs-dark)' } },
                tooltip: {
                  callbacks: {
                    label: function(context) {
                      let label = context.label || ''
                      if (label) label += ': '
                      if (context.parsed !== null) label += context.parsed + ' spots'
                      return label
                    }
                  }
                }
              },
              cutout: '70%'
            }
          })
          }
        } catch (err) {
          console.error('Error creating Parking Spot Status chart:', err)
        }
      }

      // 4. Reservation Status Breakdown (Bar) - using real data from backend
      const reservationStatusCtx = document.getElementById('reservationStatusChart')
      console.log('reservationStatusCtx element:', reservationStatusCtx)
      if (reservationStatusCtx) {
        try {
          const reservationStatus = summaryData.reservation_status || {}
          const pendingCount = reservationStatus.pending || 0
        const activeCount = reservationStatus.active || 0
        const completedCount = reservationStatus.completed || 0
        const cancelledCount = reservationStatus.cancelled || 0
        
        this.charts.reservationStatus = new Chart(reservationStatusCtx, {
          type: 'bar',
          data: {
            labels: ['Pending', 'Active', 'Completed', 'Cancelled'],
            datasets: [{
              label: 'Number of Reservations',
              data: [pendingCount, activeCount, completedCount, cancelledCount],
              backgroundColor: [
                'hsl(200, 70%, 45%)',   // Blue - Pending
                'hsl(140, 60%, 40%)',   // Green - Active
                'hsl(210, 10%, 60%)',   // Gray - Completed
                'hsl(0, 70%, 50%)'      // Red - Cancelled
              ],
              borderColor: [
                'hsl(200, 70%, 35%)',
                'hsl(140, 60%, 30%)',
                'hsl(210, 10%, 50%)',
                'hsl(0, 70%, 40%)'
              ],
              borderWidth: 1
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: { display: false },
              tooltip: {
                callbacks: {
                  label: function(context) {
                    return context.dataset.label + ': ' + context.parsed.y
                  }
                }
              }
            },
            scales: {
              y: {
                beginAtZero: true,
                ticks: {
                  callback: function(value) {
                    if (Number.isInteger(value)) return value
                  },
                  color: 'var(--bs-dark)'
                },
                grid: { color: 'rgba(0,0,0,0.1)' }
              },
              x: {
                ticks: { color: 'var(--bs-dark)' },
                grid: { color: 'rgba(0,0,0,0.1)' }
              }
            }
          }
        })
        console.log('Reservation Status chart created')
      } catch (err) {
        console.error('Error creating Reservation Status chart:', err)
      }
      }
      
      console.log('All charts initialized:', Object.keys(this.charts))
    },

    getLast7Days() {
      const dates = []
      for (let i = 6; i >= 0; i--) {
        const date = new Date()
        date.setDate(date.getDate() - i)
        dates.push(date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }))
      }
      return dates
    },

    refreshData() {
      this.loadStats()
    }
  },

  async mounted() {
    await this.loadStats()
  },

  beforeUnmount() {
    Object.values(this.charts).forEach(chart => {
      if (chart) chart.destroy()
    })
  }
}
</script>

<style scoped>
.chart-container {
  position: relative;
  height: 280px;
  width: 100%;
}

.card {
  border: none;
}

.card-header.bg-primary {
  border-bottom: none;
}

.card-header.bg-primary h5 {
  font-weight: 600;
  color: white;
  font-size: 0.95rem;
}

.card-header {
  background-color: #f8f9fa;
  border-bottom: 1px solid #e3e6f0;
  padding: 0.75rem 1rem;
  font-weight: 600;
  color: #495057;
  font-size: 0.95rem;
}
</style>

<template>
  <div class="container-fluid py-4">
    <!-- Header -->
    <div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-2 pb-2 border-bottom">
      <h1 class="h2 text-primary">Your Parking Summary</h1>
      <button @click="refreshData" class="btn btn-sm btn-outline-primary" :disabled="loading">
        <i class="fas fa-sync-alt me-1" :class="{ 'fa-spin': loading }"></i>
        Refresh
      </button>
    </div>

    <!-- Quick Stats Cards -->
    <div class="row mt-4 mb-4">
      <div class="col-lg-3 col-md-6 col-sm-6 mb-3">
        <div class="card bg-white text-dark shadow-sm h-100">
          <div class="card-body d-flex flex-column justify-content-between">
            <h6 class="card-title mb-0 text-primary" style="font-size: 0.85rem;">Total Bookings</h6>
            <p class="card-text fs-4 text-dark text-end mt-2">{{ userStats.total_reservations || 0 }}</p>
          </div>
        </div>
      </div>

      <div class="col-lg-3 col-md-6 col-sm-6 mb-3">
        <div class="card bg-white text-dark shadow-sm h-100">
          <div class="card-body d-flex flex-column justify-content-between">
            <h6 class="card-title mb-0 text-success" style="font-size: 0.85rem;">Completed</h6>
            <p class="card-text fs-4 text-dark text-end mt-2">{{ userStats.completed_reservations || 0 }}</p>
          </div>
        </div>
      </div>

      <div class="col-lg-3 col-md-6 col-sm-6 mb-3">
        <div class="card bg-white text-dark shadow-sm h-100">
          <div class="card-body d-flex flex-column justify-content-between">
            <h6 class="card-title mb-0 text-warning" style="font-size: 0.85rem;">Active</h6>
            <p class="card-text fs-4 text-dark text-end mt-2">{{ userStats.active_reservations || 0 }}</p>
          </div>
        </div>
      </div>

      <div class="col-lg-3 col-md-6 col-sm-6 mb-3">
        <div class="card bg-white text-dark shadow-sm h-100">
          <div class="card-body d-flex flex-column justify-content-between">
            <h6 class="card-title mb-0 text-info" style="font-size: 0.85rem;">Total Spent</h6>
            <p class="card-text fs-5 text-dark text-end mt-2">₹{{ userStats.total_spent || 0 }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Charts Section (V1 Style) -->
    <div class="row mt-4">
      <div v-if="loading" class="col-12 text-center py-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
      </div>
      <template v-else>
        <!-- Parking Cost Trend Chart -->
        <div class="col-lg-4 col-md-6 mb-4">
          <div class="card h-100 shadow-sm">
            <div class="card-header">Parking Cost Trend (Last 10)</div>
            <div class="card-body d-flex justify-content-center align-items-center">
              <div class="chart-container">
                <canvas id="parkingCostChart"></canvas>
              </div>
            </div>
          </div>
        </div>

        <!-- Parking Frequency Chart -->
        <div class="col-lg-4 col-md-6 mb-4">
          <div class="card h-100 shadow-sm">
            <div class="card-header">Parking Frequency (Last 7 Days)</div>
            <div class="card-body d-flex justify-content-center align-items-center">
              <div class="chart-container">
                <canvas id="parkingFrequencyChart"></canvas>
              </div>
            </div>
          </div>
        </div>

        <!-- Most Visited Lots Chart -->
        <div class="col-lg-4 col-md-12 mb-4">
          <div class="card h-100 shadow-sm">
            <div class="card-header">Most Visited Lots (Last 10)</div>
            <div class="card-body d-flex justify-content-center align-items-center">
              <div class="chart-container">
                <canvas id="mostVisitedLotsChart"></canvas>
              </div>
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
  name: 'UserSummary',
  data() {
    return {
      loading: true,
      userStats: {
        total_reservations: 0,
        completed_reservations: 0,
        active_reservations: 0,
        total_spent: 0
      },
      userReservations: [],
      charts: {}
    }
  },

  methods: {
    ...mapActions(['setAlert']),

    async loadStats() {
      try {
        this.loading = true

        const [reservationsRes, statsRes] = await Promise.all([
          this.$api.user.getReservations(),
          this.$api.user.getDashboard()
        ])

        this.userReservations = Array.isArray(reservationsRes.data) ? reservationsRes.data : []
        this.userStats = statsRes.data || this.userStats

        this.$nextTick(() => {
          this.initCharts()
        })
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

    initCharts() {
      // Destroy existing charts
      Object.values(this.charts).forEach(chart => {
        if (chart) chart.destroy()
      })
      this.charts = {}

      // Helper function for no data display
      const handleNoData = (chartId, parentDiv) => {
        const ctx = document.getElementById(chartId)
        if (ctx) {
          parentDiv.innerHTML = `<div class="alert alert-info text-center mt-3" role="alert">No data available to display this chart yet.</div>`
          parentDiv.style.display = 'flex'
          parentDiv.style.flexDirection = 'column'
          parentDiv.style.justifyContent = 'center'
          parentDiv.style.alignItems = 'center'
          ctx.remove()
        }
      }

      // 1. Parking Cost Trend Chart (Line - Last 10)
      const parkingCostCtx = document.getElementById('parkingCostChart')
      if (parkingCostCtx) {
        const costTrendData = this.getParkingCostTrend()
        if (costTrendData.labels.length > 0 && costTrendData.values.some(v => v > 0)) {
          this.charts.cost = new Chart(parkingCostCtx, {
            type: 'line',
            data: {
              labels: costTrendData.labels,
              datasets: [{
                label: 'Parking Cost (₹)',
                data: costTrendData.values,
                backgroundColor: 'rgba(75, 192, 192, 0.5)',
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 1
              }]
            },
            options: {
              scales: {
                y: {
                  beginAtZero: true,
                  ticks: {
                    callback: function(value) {
                      return '₹' + value
                    }
                  }
                }
              },
              responsive: true,
              maintainAspectRatio: false,
              plugins: {
                legend: { display: false },
                tooltip: {
                  callbacks: {
                    label: function(context) {
                      return context.dataset.label + ': ₹' + context.parsed.y.toFixed(2)
                    }
                  }
                }
              }
            }
          })
        } else {
          handleNoData('parkingCostChart', parkingCostCtx.parentElement)
        }
      }

      // 2. Parking Frequency Chart (Bar - Last 7 Days)
      const parkingFrequencyCtx = document.getElementById('parkingFrequencyChart')
      if (parkingFrequencyCtx) {
        const frequencyData = this.getParkingFrequency()
        if (frequencyData.labels.length > 0 && frequencyData.values.some(v => v > 0)) {
          this.charts.frequency = new Chart(parkingFrequencyCtx, {
            type: 'bar',
            data: {
              labels: frequencyData.labels,
              datasets: [{
                label: 'Parking Count',
                data: frequencyData.values,
                backgroundColor: 'rgba(153, 102, 255, 0.5)',
                borderColor: 'rgba(153, 102, 255, 1)',
                borderWidth: 1
              }]
            },
            options: {
              scales: {
                y: {
                  beginAtZero: true,
                  ticks: {
                    stepSize: 1,
                    callback: function(value) {
                      if (Number.isInteger(value)) {
                        return value
                      }
                    }
                  }
                }
              },
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
              }
            }
          })
        } else {
          handleNoData('parkingFrequencyChart', parkingFrequencyCtx.parentElement)
        }
      }

      // 3. Most Visited Lots Chart (Doughnut - Last 10)
      const mostVisitedCtx = document.getElementById('mostVisitedLotsChart')
      if (mostVisitedCtx) {
        const lotData = this.getMostVisitedLots()
        if (lotData.labels.length > 0) {
          this.charts.mostVisited = new Chart(mostVisitedCtx, {
            type: 'doughnut',
            data: {
              labels: lotData.labels,
              datasets: [{
                data: lotData.values,
                backgroundColor: [
                  '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40', '#50C878', '#C0C0C0'
                ],
                hoverOffset: 4
              }]
            },
            options: {
              responsive: true,
              maintainAspectRatio: false,
              plugins: {
                legend: { position: 'top' },
                tooltip: {
                  callbacks: {
                    label: function(context) {
                      let label = context.label || ''
                      if (label) label += ': '
                      if (context.parsed !== null) label += context.parsed
                      return label
                    }
                  }
                }
              }
            }
          })
        } else {
          handleNoData('mostVisitedLotsChart', mostVisitedCtx.parentElement)
        }
      }
    },

    getParkingCostTrend() {
      // Get last 10 completed reservations with cost
      const costData = this.userReservations
        .filter(r => r.status === 'completed' && r.parking_cost)
        .slice(-10)
        .map((r, idx) => ({
          label: `Booking ${idx + 1}`,
          cost: r.parking_cost
        }))

      return {
        labels: costData.map(d => d.label),
        values: costData.map(d => d.cost)
      }
    },

    getParkingFrequency() {
      // Count bookings by day for last 7 days
      const last7Days = []
      for (let i = 6; i >= 0; i--) {
        const date = new Date()
        date.setDate(date.getDate() - i)
        last7Days.push(date.toLocaleDateString('en-US', { weekday: 'short' }))
      }

      const bookingsByDay = {}
      last7Days.forEach(day => {
        bookingsByDay[day] = 0
      })

      this.userReservations.forEach(r => {
        const date = new Date(r.booking_timestamp)
        const day = date.toLocaleDateString('en-US', { weekday: 'short' })
        if (bookingsByDay.hasOwnProperty(day)) {
          bookingsByDay[day]++
        }
      })

      return {
        labels: last7Days,
        values: last7Days.map(day => bookingsByDay[day] || 0)
      }
    },

    getMostVisitedLots() {
      // Count visits to each lot (last 10 unique lots visited)
      const lotCounts = {}

      this.userReservations.slice(-100).forEach(r => {
        const lotName = r.lot_name || 'Unknown'
        lotCounts[lotName] = (lotCounts[lotName] || 0) + 1
      })

      const sorted = Object.entries(lotCounts)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 10)

      return {
        labels: sorted.map(([name]) => name),
        values: sorted.map(([, count]) => count)
      }
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

.card-header {
  background-color: #f8f9fa;
  border-bottom: 1px solid #e3e6f0;
  padding: 0.75rem 1rem;
  font-weight: 600;
  color: #495057;
  font-size: 0.95rem;
}
</style>

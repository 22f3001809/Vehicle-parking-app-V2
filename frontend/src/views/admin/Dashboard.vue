<template>
  <div class="container-fluid py-3">
    <!-- Header -->
    <div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-2 pb-2 border-bottom">
      <h1 class="h2 text-primary">Admin Dashboard</h1>
      <div class="btn-toolbar mb-2 mb-md-0">
        <router-link to="/admin/parking-lots/create" class="btn btn-sm btn-outline-primary">
          <i class="fas fa-plus-circle me-1"></i>
          Create New Parking Lot
        </router-link>
      </div>
    </div>

    <!-- Quick Stats Cards -->
    <div class="row mt-4">
      <div class="col-lg-2 col-md-4 col-sm-6 mb-3">
        <div class="card bg-white text-dark shadow-sm h-100">
          <div class="card-body d-flex flex-column justify-content-between">
            <h5 class="card-title mb-0 text-primary" style="font-size: 0.9rem;">Total Parking Lots</h5>
            <p class="card-text fs-4 text-dark text-end mt-2">{{ stats.totalLots || 0 }}</p>
          </div>
        </div>
      </div>

      <div class="col-lg-2 col-md-4 col-sm-6 mb-3">
        <div class="card bg-white text-dark shadow-sm h-100">
          <div class="card-body d-flex flex-column justify-content-between">
            <h5 class="card-title mb-0 text-primary" style="font-size: 0.9rem;">Total Parking Spots</h5>
            <p class="card-text fs-4 text-dark text-end mt-2">{{ stats.totalSpots || 0 }}</p>
          </div>
        </div>
      </div>

      <div class="col-lg-2 col-md-4 col-sm-6 mb-3">
        <div class="card bg-white text-dark shadow-sm h-100">
          <div class="card-body d-flex flex-column justify-content-between">
            <h5 class="card-title mb-0 text-success" style="font-size: 0.9rem;">Available Spots</h5>
            <p class="card-text fs-4 text-dark text-end mt-2">{{ stats.availableSpots || 0 }}</p>
          </div>
        </div>
      </div>

      <div class="col-lg-2 col-md-4 col-sm-6 mb-3">
        <div class="card bg-white text-dark shadow-sm h-100">
          <div class="card-body d-flex flex-column justify-content-between">
            <h5 class="card-title mb-0 text-danger" style="font-size: 0.9rem;">Occupied Spots</h5>
            <p class="card-text fs-4 text-dark text-end mt-2">{{ stats.occupiedSpots || 0 }}</p>
          </div>
        </div>
      </div>

      <div class="col-lg-2 col-md-4 col-sm-6 mb-3">
        <div class="card bg-white text-dark shadow-sm h-100">
          <div class="card-body d-flex flex-column justify-content-between">
            <h5 class="card-title mb-0 text-info" style="font-size: 0.9rem;">Pending Reservations</h5>
            <p class="card-text fs-4 text-dark text-end mt-2">{{ stats.pendingReservations || 0 }}</p>
          </div>
        </div>
      </div>

      <div class="col-lg-2 col-md-4 col-sm-6 mb-3">
        <div class="card bg-white text-dark shadow-sm h-100">
          <div class="card-body d-flex flex-column justify-content-between">
            <h5 class="card-title mb-0 text-info" style="font-size: 0.9rem;">Total Users</h5>
            <p class="card-text fs-4 text-dark text-end mt-2">{{ stats.totalUsers || 0 }}</p>
          </div>
        </div>
      </div>

      <div class="col-lg-2 col-md-4 col-sm-6 mb-3">
        <div class="card bg-white text-dark shadow-sm h-100">
          <div class="card-body d-flex flex-column justify-content-between">
            <h5 class="card-title mb-0 text-warning" style="font-size: 0.9rem;">Total Revenue</h5>
            <p class="card-text fs-4 text-dark text-end mt-2">₹{{ stats.totalRevenue || 0 }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Recent Activity -->
    <div class="row mt-4">
      <div class="col-md-6">
        <div class="card shadow-sm">
          <div class="card-header">
            <h5 class="mb-0">Recent Parking Lots</h5>
          </div>
          <div class="card-body">
            <div v-if="loading" class="text-center">
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
            </div>
            <div v-else-if="recentLots.length === 0" class="text-center text-muted py-4">
              <i class="fas fa-parking fa-3x mb-3"></i>
              <p>No parking lots created yet.</p>
              <router-link to="/admin/parking-lots/create" class="btn btn-primary">
                <i class="fas fa-plus me-2"></i>
                Create First Lot
              </router-link>
            </div>
            <div v-else class="table-responsive">
              <table class="table table-sm">
                <thead>
                  <tr>
                    <th>Name</th>
                    <th>Spots</th>
                    <th>Available</th>
                    <th>Rate</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="lot in recentLots" :key="lot.id">
                    <td>{{ lot.name }}</td>
                    <td>{{ lot.number_of_spots }}</td>
                    <td>{{ lot.available_spots }}</td>
                    <td>₹{{ lot.price_per_hour }}/hr</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

      <div class="col-md-6">
        <div class="card shadow-sm">
          <div class="card-header">
            <h5 class="mb-0">Recent Users</h5>
          </div>
          <div class="card-body">
            <div v-if="loading" class="text-center">
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
            </div>
            <div v-else-if="recentUsers.length === 0" class="text-center text-muted py-4">
              <i class="fas fa-users fa-3x mb-3"></i>
              <p>No users registered yet.</p>
            </div>
            <div v-else class="table-responsive">
              <table class="table table-sm">
                <thead>
                  <tr>
                    <th>Username</th>
                    <th>Email</th>
                    <th>Joined</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="user in recentUsers" :key="user.id">
                    <td>{{ user.username }}</td>
                    <td>{{ user.email }}</td>
                    <td>{{ formatDate(user.created_at) }}</td>
                  </tr>
                </tbody>
              </table>
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
  name: 'AdminDashboard',
  data() {
    return {
      loading: true,
      stats: {
        totalLots: 0,
        totalSpots: 0,
        availableSpots: 0,
        occupiedSpots: 0,
        totalUsers: 0,
        totalRevenue: 0
      },
      recentLots: [],
      recentUsers: []
    }
  },
  
  computed: {
    ...mapState(['user'])
  },
  
  methods: {
    ...mapActions(['setAlert', 'setLoading']),
    
    async loadStats() {
      try {
        this.loading = true
        
  // Load admin dashboard data (baseURL already includes /api)
  const response = await this.$api.admin.getDashboard()
        const data = response.data
        
        this.stats = {
          totalLots: data.total_lots || 0,
          totalSpots: data.total_spots || 0,
          availableSpots: data.available_spots || 0,
          occupiedSpots: data.occupied_spots || 0,
          reservedSpots: data.reserved_spots || 0,
          pendingReservations: data.pending_reservations || 0,
          totalUsers: data.total_users || 0,
          totalRevenue: data.total_revenue || 0
        }
        
        this.recentLots = data.recent_lots || []
        this.recentUsers = data.recent_users || []
        
      } catch (error) {
        console.error('Error loading admin dashboard:', error)
        this.setAlert({
          message: 'Failed to load dashboard data',
          type: 'error'
        })
      } finally {
        this.loading = false
      }
    },
    
    formatDate(dateString) {
      if (!dateString) return 'N/A'
      return new Date(dateString).toLocaleDateString()
    }
  },
  
  async mounted() {
    await this.loadStats()
  }
}
</script>
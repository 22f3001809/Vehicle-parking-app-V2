<template>
  <div class="container-fluid py-4">
    <h2><i class="fas fa-calendar-alt me-2"></i>Reservations Management</h2>
    <p class="text-muted">View and manage all parking reservations</p>
    
    <div class="card">
      <div class="card-body">
        <div class="table-responsive">
          <table class="table table-striped">
            <thead>
              <tr>
                <th>ID</th>
                <th>User</th>
                <th>Parking Lot</th>
                <th>Spot</th>
                <th>Start Time</th>
                <th>End Time</th>
                <th>Status</th>
                <th>Amount</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="loading">
                <td colspan="9" class="text-center py-4">
                  <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                  </div>
                </td>
              </tr>
              <tr v-else-if="reservations.length === 0">
                <td colspan="9" class="text-center py-4 text-muted">
                  No reservations found
                </td>
              </tr>
              <tr v-else v-for="reservation in reservations" :key="reservation.id">
                <td>{{ reservation.id }}</td>
                <td>{{ reservation.username || 'N/A' }}</td>
                <td>
                  {{ reservation.lot_name }}
                  <small v-if="reservation.lot_deleted" class="text-danger d-block">(Inactive/Deleted)</small>
                </td>
                <td>
                  {{ reservation.spot_number }}
                  <small v-if="reservation.spot_deleted" class="text-danger d-block" style="font-size: 0.7rem;">(Deleted)</small>
                </td>
                <td>{{ formatDateTime(reservation.booking_timestamp) }}</td>
                <td>{{ reservation.check_out_timestamp ? formatDateTime(reservation.check_out_timestamp) : '-' }}</td>
                <td>
                  <span :class="getStatusBadgeClass(reservation.status)" class="badge">
                    {{ reservation.status }}
                  </span>
                </td>
                <td>{{ reservation.parking_cost ? '₹' + reservation.parking_cost : '-' }}</td>
                <td>
                  <button class="btn btn-sm btn-outline-info">
                    <i class="fas fa-eye"></i>
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapActions } from 'vuex'

export default {
  name: 'AdminReservations',
  data() {
    return {
      reservations: [],
      loading: false
    }
  },
  methods: {
    ...mapActions(['setAlert']),
    
    async loadReservations() {
      try {
        this.loading = true
        const response = await this.$api.admin.getAllReservations()
        this.reservations = response.data || []
      } catch (error) {
        console.error('Error loading reservations:', error)
        this.setAlert({
          message: 'Failed to load reservations',
          type: 'error'
        })
      } finally {
        this.loading = false
      }
    },
    
    formatDateTime(dateTime) {
      return this.$formatDateTime(dateTime)
    },
    
    getStatusBadgeClass(status) {
      const classes = {
        'active': 'bg-success',
        'pending': 'bg-warning',
        'completed': 'bg-primary',
        'cancelled': 'bg-danger'
      }
      return classes[status] || 'bg-secondary'
    }
  },
  
  async mounted() {
    await this.loadReservations()
  }
}
</script>
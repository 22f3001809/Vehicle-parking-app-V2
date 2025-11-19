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
              <tr v-for="reservation in reservations" :key="reservation.id">
                <td>{{ reservation.id }}</td>
                <td>{{ reservation.user.username }}</td>
                <td>{{ reservation.parking_lot.name }}</td>
                <td>{{ reservation.spot.number }}</td>
                <td>{{ formatDateTime(reservation.start_time) }}</td>
                <td>{{ formatDateTime(reservation.end_time) }}</td>
                <td>
                  <span :class="getStatusBadgeClass(reservation.status)" class="badge">
                    {{ reservation.status }}
                  </span>
                </td>
                <td>₹{{ reservation.total_amount }}</td>
                <td>
                  <button class="btn btn-sm btn-outline-primary">
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
export default {
  name: 'AdminReservations',
  data() {
    return {
      reservations: []
    }
  },
  methods: {
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
  }
}
</script>
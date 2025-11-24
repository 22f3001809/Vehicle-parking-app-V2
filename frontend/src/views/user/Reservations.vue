<template>
  <div class="container-fluid py-4">
    <h2>My Reservations</h2>
    <p class="text-muted">View and manage your parking reservations</p>
    
    <div class="card shadow-sm">
      <div class="card-body">
        <div class="table-responsive">
          <table class="table table-hover">
            <thead class="table-light">
              <tr>
                <th>ID</th>
                <th>Parking Lot</th>
                <th>Spot</th>
                <th>Vehicle</th>
                <th>Booked At</th>
                <th>Check-In Time</th>
                <th>Check-Out Time</th>
                <th>Status</th>
                <th>Cost</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="loading">
                <td colspan="10" class="text-center py-4">
                  <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                  </div>
                  <p class="mt-2 text-muted">Loading reservations...</p>
                </td>
              </tr>
              <tr v-else-if="reservations.length === 0">
                <td colspan="10" class="text-center py-5">
                  <p class="text-muted">No reservations found</p>
                  <router-link to="/parking-lots" class="btn btn-primary mt-2">
                    Book Your First Parking
                  </router-link>
                </td>
              </tr>
              <tr v-else v-for="reservation in reservations" :key="reservation.id">
                <td>{{ reservation.id }}</td>
                <td>{{ reservation.lot_name || 'N/A' }}</td>
                <td>
                  <span class="badge bg-secondary">{{ reservation.spot_number || 'N/A' }}</span>
                </td>
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
                <td>{{ reservation.parking_cost ? '₹' + reservation.parking_cost : '-' }}</td>
                <td class="text-nowrap">
                  <!-- Pending: Can Check In or Cancel -->
                  <button v-if="reservation.status === 'pending'" 
                          class="btn btn-sm btn-success me-1"
                          @click="checkIn(reservation.id)"
                          :disabled="processing">
                    <i class="fas fa-sign-in-alt me-1"></i>Check In
                  </button>
                  <button v-if="reservation.status === 'pending'" 
                          class="btn btn-sm btn-outline-danger"
                          @click="cancelReservation(reservation.id)"
                          :disabled="processing">
                    <i class="fas fa-times me-1"></i>Cancel
                  </button>
                  
                  <!-- Active: Can Check Out -->
                  <button v-if="reservation.status === 'active'" 
                          class="btn btn-sm btn-primary"
                          @click="checkOut(reservation.id)"
                          :disabled="processing">
                    <i class="fas fa-sign-out-alt me-1"></i>Check Out
                  </button>
                  
                  <!-- Completed/Cancelled: No actions -->
                  <span v-if="reservation.status === 'completed' || reservation.status === 'cancelled'" 
                        class="text-muted">
                    -
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
    <CheckoutModal :details="checkoutDetails" @confirmed="confirmCheckout" />
  </div>
</template>

<script>
import CheckoutModal from '@/components/CheckoutModal.vue';
import { Modal } from 'bootstrap';

export default {
  name: 'UserReservations',
  components: {
    CheckoutModal
  },
  data() {
    return {
      reservations: [],
      loading: false,
      processing: false,
      checkoutDetails: {
        cost: 0,
        duration: 'N/A'
      },
      selectedReservationId: null,
      checkoutModalInstance: null
    }
  },
  methods: {
    formatDateTime(dateTime) {
      return this.$formatDateTime(dateTime)
    },
    getStatusBadgeClass(status) {
      const classes = {
        'active': 'bg-success',
        'pending': 'bg-warning text-dark',
        'completed': 'bg-info',
        'cancelled': 'bg-danger'
      }
      return classes[status] || 'bg-secondary'
    },
    
    async loadReservations() {
      try {
        this.loading = true
        const response = await this.$api.user.getReservations()
        // Backend returns array directly
        this.reservations = Array.isArray(response.data) ? response.data : (response.data.reservations || [])
      } catch (error) {
        console.error('Error loading reservations:', error)
        this.$store.dispatch('setAlert', {
          message: 'Failed to load reservations',
          type: 'error'
        })
      } finally {
        this.loading = false
      }
    },
    
    async checkIn(reservationId) {
      if (!confirm('Are you sure you want to check in to this parking spot?')) return
      
      this.processing = true
      try {
        await this.$api.user.checkIn(reservationId)
        this.$store.dispatch('setAlert', {
          message: 'Checked in successfully! Parking cost will be calculated from now.',
          type: 'success'
        })
        await this.loadReservations()
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
      this.processing = true;
      this.selectedReservationId = reservationId;
      try {
        const response = await this.$api.user.getCheckoutDetails(reservationId);
        this.checkoutDetails = response.data;
        this.checkoutModalInstance.show();
      } catch (error) {
        console.error('Error fetching checkout details:', error);
        this.$store.dispatch('setAlert', {
          message: error.response?.data?.error || 'Failed to get checkout details',
          type: 'error'
        });
      } finally {
        this.processing = false;
      }
    },

    async confirmCheckout() {
      this.checkoutModalInstance.hide();
      this.processing = true;
      try {
        await this.$api.user.checkOut(this.selectedReservationId);
        this.$store.dispatch('setAlert', {
          message: 'Checked out successfully! Please proceed to payment.',
          type: 'success'
        });
        await this.loadReservations();
      } catch (error) {
        console.error('Error checking out:', error);
        this.$store.dispatch('setAlert', {
          message: error.response?.data?.error || 'Failed to check out',
          type: 'error'
        });
      } finally {
        this.processing = false;
        this.selectedReservationId = null;
      }
    },
    
    async cancelReservation(id) {
      if (!confirm('Are you sure you want to cancel this reservation?')) return
      
      this.processing = true
      try {
        await this.$api.user.cancelReservation(id)
        this.$store.dispatch('setAlert', {
          message: 'Reservation cancelled successfully',
          type: 'success'
        })
        await this.loadReservations()
      } catch (error) {
        console.error('Error cancelling reservation:', error)
        this.$store.dispatch('setAlert', {
          message: error.response?.data?.error || 'Failed to cancel reservation',
          type: 'error'
        })
      } finally {
        this.processing = false
      }
    }
  },
  
  async mounted() {
    await this.loadReservations();
    this.checkoutModalInstance = new Modal(document.getElementById('checkoutModal'));
  }
}
</script>

<style scoped>
.table th {
  font-weight: 600;
  border-top: none;
}

.btn-sm {
  padding: 0.25rem 0.5rem;
  font-size: 0.875rem;
}
</style>
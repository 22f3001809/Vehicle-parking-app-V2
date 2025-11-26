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
              <tr v-else v-for="reservation in reservations" :key="reservation.id" 
                  :class="{'table-active': reservation.status === 'active'}">
                <td>{{ reservation.id }}</td>
                <td>
                  {{ reservation.lot_name }}
                  <small v-if="reservation.lot_deleted" class="text-danger d-block">(Inactive/Deleted)</small>
                </td>
                <td>
                  <span class="badge bg-secondary">{{ reservation.spot_number }}</span>
                  <small v-if="reservation.spot_deleted" class="text-danger d-block" style="font-size: 0.7rem;">(Deleted)</small>
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
                  <span :class="getStatusBadgeClass(reservation.status)" class="badge text-capitalize">
                    {{ reservation.status }}
                  </span>
                </td>
                <td>{{ reservation.parking_cost ? '₹' + reservation.parking_cost : '-' }}</td>
                <td class="text-nowrap" @click.stop>
                  <!-- Pending: Can Check In or Cancel -->
                  <button v-if="reservation.status === 'pending'" 
                          class="btn btn-xs btn-success me-1 px-2 py-1"
                          style="font-size: 0.75rem;"
                          @click="checkIn(reservation.id)"
                          :disabled="processing">
                    Check In
                  </button>
                  <button v-if="reservation.status === 'pending'" 
                          class="btn btn-xs btn-outline-danger px-2 py-1"
                          style="font-size: 0.75rem;"
                          @click="cancelReservation(reservation.id)"
                          :disabled="processing">
                    Cancel
                  </button>
                  
                  <!-- Active: Can Park Out -->
                  <button v-if="reservation.status === 'active'" 
                          class="btn btn-xs btn-primary px-2 py-1"
                          style="font-size: 0.75rem;"
                          @click="checkOut(reservation.id)"
                          :disabled="processing">
                    Park Out
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
    <!-- Checkout Confirmation Modal -->
    <div class="modal fade" id="checkoutModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Confirm Park Out</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <div class="alert alert-info">
              <h6 class="mb-3">Parking Summary</h6>
              <div class="row">
                <div class="col-6"><strong>Spot:</strong></div>
                <div class="col-6">{{ checkoutDetails.spot_id }}</div>
              </div>
              <div class="row">
                <div class="col-6"><strong>Vehicle:</strong></div>
                <div class="col-6">{{ checkoutDetails.vehicle_number }}</div>
              </div>
              <div class="row">
                <div class="col-6"><strong>Check-in:</strong></div>
                <div class="col-6">{{ checkoutDetails.check_in_time }}</div>
              </div>
              <div class="row">
                <div class="col-6"><strong>Duration:</strong></div>
                <div class="col-6">{{ checkoutDetails.duration }}</div>
              </div>
              <hr>
              <div class="row">
                <div class="col-6"><strong class="fs-5">Total Cost:</strong></div>
                <div class="col-6"><strong class="fs-5 text-success">₹{{ checkoutDetails.cost }}</strong></div>
              </div>
            </div>
            <p class="mb-0">Are you sure you want to park out?</p>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
            <button type="button" class="btn btn-primary" @click="confirmCheckout" :disabled="processing">
              <span v-if="processing" class="spinner-border spinner-border-sm me-1"></span>
              Confirm Park Out
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { Modal } from 'bootstrap';

export default {
  name: 'UserReservations',
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

.cursor-pointer {
  cursor: pointer;
}

.table-active {
  background-color: rgba(13, 110, 253, 0.05) !important;
}

tr.cursor-pointer:hover {
  background-color: rgba(13, 110, 253, 0.1) !important;
}
</style>
<template>
  <div class="container py-4">
    <div class="row mb-4">
      <div class="col-12">
        <h2 class="h3 mb-2">Book Parking Spot</h2>
        <p class="text-muted mb-0">Reserve your parking spot</p>
      </div>
    </div>
    
    <div class="row g-4" v-if="!loading && parkingLot">
      <div class="col-12 col-lg-8">
        <div class="card shadow-sm h-100">
          <div class="card-header bg-primary text-white">
            <h5 class="mb-1">{{ parkingLot.name }}</h5>
            <small class="d-block">{{ parkingLot.address }}</small>
          </div>
          <div class="card-body">
            <div class="alert alert-info mb-4">
              <div class="row g-3">
                <div class="col-6 col-md-6">
                  <div class="d-flex align-items-center">
                    <div>
                      <small class="d-block text-muted">Available Spots</small>
                      <strong class="fs-5">{{ parkingLot.available_spots }} / {{ parkingLot.number_of_spots }}</strong>
                    </div>
                  </div>
                </div>
                <div class="col-6 col-md-6">
                  <div class="d-flex align-items-center">
                    <div>
                      <small class="d-block text-muted">Rate per Hour</small>
                      <strong class="fs-5">₹{{ parkingLot.price_per_hour }}</strong>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <form @submit.prevent="bookSpot" v-if="parkingLot.available_spots > 0">
              <div class="row">
                <div class="col-12 mb-4">
                  <label class="form-label fw-bold">Vehicle Number <span class="text-danger">*</span></label>
                  <input type="text" 
                         class="form-control form-control-lg" 
                         v-model="booking.vehicleNumber" 
                         placeholder="e.g., MH 01 AB 1234" 
                         required
                         :class="{ 'is-invalid': errors.vehicleNumber }">
                  <div class="form-text">Enter your vehicle registration number</div>
                  <div v-if="errors.vehicleNumber" class="invalid-feedback">{{ errors.vehicleNumber }}</div>
                </div>
              </div>
              
              <!-- Cost Estimator -->
              <div class="row">
                <div class="col-12 mb-4">
                  <div class="card border-success">
                    <div class="card-header bg-success bg-opacity-10">
                      <h6 class="mb-0">Cost Estimator</h6>
                    </div>
                    <div class="card-body">
                      <div class="row align-items-center">
                        <div class="col-md-6 mb-3 mb-md-0">
                          <label class="form-label">Estimated Parking Duration (hours)</label>
                          <input type="number" 
                                 class="form-control" 
                                 v-model.number="estimatedHours" 
                                 min="1" 
                                 step="0.5"
                                 placeholder="Enter hours">
                        </div>
                        <div class="col-md-6">
                          <div class="text-center p-3 bg-light rounded">
                            <small class="d-block text-muted">Estimated Cost</small>
                            <h4 class="mb-0 text-success">
                              ₹{{ estimatedCost }}
                            </h4>
                            <small class="text-muted">
                              ({{ estimatedHours }} hours × ₹{{ parkingLot.price_per_hour }}/hour)
                            </small>
                          </div>
                        </div>
                      </div>
                      <div class="alert alert-info mt-3 mb-0">
                        <small>
                          This is an estimate. Final cost will be calculated based on actual parking duration.
                        </small>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              
              <div class="d-grid gap-2 d-md-flex">
                <button type="submit" 
                        class="btn btn-primary btn-lg flex-grow-1" 
                        :disabled="!booking.vehicleNumber || bookingLoading">
                  {{ bookingLoading ? 'Processing...' : 'Confirm Booking' }}
                </button>
                <router-link to="/parking-lots" class="btn btn-outline-secondary btn-lg">
                  Back
                </router-link>
              </div>
            </form>
            
            <div v-else class="text-center py-5">
              <h4 class="text-danger mb-3">No Available Spots</h4>
              <p class="text-muted mb-4">This parking lot is currently full. Please try another location.</p>
              <router-link to="/parking-lots" class="btn btn-primary btn-lg">
                Find Another Lot
              </router-link>
            </div>
          </div>
        </div>
      </div>
      
      <div class="col-12 col-lg-4">
        <div class="card shadow-sm h-100">
          <div class="card-header bg-light">
            <h5 class="mb-0">Booking Details</h5>
          </div>
          <div class="card-body">
            <div class="mb-4">
              <div class="d-flex align-items-start mb-2">
                <div>
                  <h6 class="mb-1 text-muted">Location</h6>
                  <p class="mb-0">{{ parkingLot.address }}</p>
                  <small class="text-muted">PIN: {{ parkingLot.pin_code }}</small>
                </div>
              </div>
            </div>
            
            <div class="mb-4">
              <div class="d-flex align-items-start mb-2">
                <div>
                  <h6 class="mb-1 text-muted">Pricing</h6>
                  <p class="mb-0 fs-5 fw-bold text-success">₹{{ parkingLot.price_per_hour }}/hour</p>
                  <small class="text-muted">Pay when you check out</small>
                </div>
              </div>
            </div>
            
            <hr>
            
            <div class="alert alert-warning mb-0">
              <small>
                <strong>Important:</strong> After booking, you must check in when you arrive at the parking lot to activate your reservation.
              </small>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div v-else-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="mt-3 text-muted">Loading parking lot details...</p>
    </div>
    
    <div v-else class="text-center py-5">
      <h4>Parking Lot Not Found</h4>
      <p class="text-muted">The requested parking lot could not be found or is no longer available.</p>
      <router-link to="/parking-lots" class="btn btn-primary">
        Back to Available Lots
      </router-link>
    </div>
  </div>
</template>

<script>
import { mapActions } from 'vuex'

export default {
  name: 'BookParking',
  data() {
    return {
      parkingLot: null,
      booking: {
        vehicleNumber: ''
      },
      loading: true,
      bookingLoading: false,
      errors: {},
      estimatedHours: 2
    }
  },
  computed: {
    estimatedCost() {
      if (!this.parkingLot || !this.estimatedHours) return 0
      return (this.parkingLot.price_per_hour * this.estimatedHours).toFixed(2)
    }
  },
  methods: {
    ...mapActions(['setAlert']),
    
    async loadParkingLot() {
      try {
        this.loading = true
        const lotId = this.$route.params.id
        
        if (!lotId) {
          this.$router.push('/parking-lots')
          return
        }
        
        const response = await this.$api.parking.getLotDetails(lotId)
        this.parkingLot = response.data
        
      } catch (error) {
        console.error('Error loading parking lot:', error)
        this.setAlert({
          message: error.response?.data?.error || 'Failed to load parking lot details',
          type: 'error'
        })
        this.parkingLot = null
      } finally {
        this.loading = false
      }
    },
    
    async bookSpot() {
      try {
        this.bookingLoading = true
        this.errors = {}
        
        // Validate
        if (!this.booking.vehicleNumber.trim()) {
          this.errors.vehicleNumber = 'Vehicle number is required'
          return
        }
        
        const response = await this.$api.user.bookSpot(this.parkingLot.id, {
          vehicle_number: this.booking.vehicleNumber.trim().toUpperCase()
        })
        
        this.setAlert({
          message: 'Parking spot booked successfully! Check your reservations to manage this booking.',
          type: 'success'
        })
        
        // Redirect to user dashboard or reservations
        this.$router.push('/user/reservations')
        
      } catch (error) {
        console.error('Booking failed:', error)
        this.setAlert({
          message: error.response?.data?.error || 'Failed to book parking spot',
          type: 'error'
        })
      } finally {
        this.bookingLoading = false
      }
    }
  },
  
  async mounted() {
    await this.loadParkingLot()
  }
}
</script>

<style scoped>
.card {
  border-radius: 0.5rem;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.card:hover {
  transform: translateY(-2px);
  box-shadow: 0 0.5rem 1.5rem rgba(0, 0, 0, 0.1) !important;
}

.form-control-lg {
  font-size: 1.1rem;
  padding: 0.75rem 1rem;
}

.btn-lg {
  padding: 0.75rem 1.5rem;
  font-size: 1.05rem;
}

@media (max-width: 768px) {
  .h3 {
    font-size: 1.5rem;
  }
  
  .btn-lg {
    font-size: 1rem;
    padding: 0.65rem 1.25rem;
  }
  
  .fs-5 {
    font-size: 1rem !important;
  }
}

.alert {
  border-radius: 0.5rem;
}

.card-header {
  border-bottom: 2px solid rgba(0,0,0,0.05);
}
</style>
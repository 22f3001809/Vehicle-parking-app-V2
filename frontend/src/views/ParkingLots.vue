<template>
  <div class="container-fluid py-4">
    <div class="row">
      <div class="col-12">
        <div class="card shadow-sm">
          <div class="card-header bg-primary text-white">
            <h4 class="mb-0">
              <i class="fas fa-car-side me-2"></i>
              Available Parking Lots
            </h4>
          </div>
          <div class="card-body">
            <div class="row" v-if="loading">
              <div class="col-12 text-center">
                <div class="spinner-border text-primary" role="status">
                  <span class="visually-hidden">Loading...</span>
                </div>
              </div>
            </div>
            <div class="row" v-else>
              <div class="col-md-4 mb-4" v-for="lot in parkingLots" :key="lot.id">
                <div class="card h-100 parking-lot-card">
                  <div class="card-body">
                    <h5 class="card-title">{{ lot.name }}</h5>
                    <p class="card-text text-muted">
                      <i class="fas fa-map-marker-alt me-1"></i>
                      {{ lot.address }}
                    </p>
                    <div class="d-flex justify-content-between align-items-center mb-3">
                      <span class="badge bg-success">{{ lot.available_spots }}/{{ lot.number_of_spots }} Available</span>
                      <span class="text-primary fw-bold">₹{{ lot.price_per_hour }}/hr</span>
                    </div>
                    <div class="progress mb-3">
                      <div class="progress-bar" 
                           :style="{ width: (lot.available_spots / lot.number_of_spots * 100) + '%' }"
                           :class="getProgressBarClass(lot.available_spots / lot.number_of_spots)">
                      </div>
                    </div>
                    <router-link :to="`/user/book-parking/${lot.id}`" 
                                 class="btn btn-primary w-100"
                                 :class="{ 'disabled': lot.available_spots === 0 }"
                                 v-if="isAuthenticated && !isAdmin">
                      <i class="fas fa-parking me-2"></i>
                      {{ lot.available_spots > 0 ? 'Book Now' : 'Full' }}
                    </router-link>
                    <router-link to="/login" 
                                 class="btn btn-primary w-100"
                                 v-else-if="!isAuthenticated">
                      <i class="fas fa-sign-in-alt me-2"></i>
                      Login to Book
                    </router-link>
                    <div v-else class="text-muted text-center">
                      <small>Available for users to book</small>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapState, mapActions, mapGetters } from 'vuex'

export default {
  name: 'ParkingLots',
  data() {
    return {
      loading: true
    }
  },
  computed: {
    ...mapState('parking', ['lots']),
    ...mapGetters(['isAuthenticated', 'isAdmin']),
    parkingLots() {
      return this.lots
    }
  },
  methods: {
    ...mapActions('parking', ['fetchLots']),
    getProgressBarClass(ratio) {
      if (ratio > 0.5) return 'bg-success'
      if (ratio > 0.2) return 'bg-warning'
      return 'bg-danger'
    }
  },
  async mounted() {
    try {
      await this.fetchLots()
    } catch (error) {
      console.error('Error loading parking lots:', error)
    } finally {
      this.loading = false
    }
  }
}
</script>

<style scoped>
.parking-lot-card {
  transition: transform 0.2s, box-shadow 0.2s;
  border: 1px solid #e3e6f0;
}

.parking-lot-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15) !important;
}

.progress {
  height: 8px;
}

.badge {
  font-size: 0.75rem;
}
</style>
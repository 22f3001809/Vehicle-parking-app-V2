<template>
  <div class="container-fluid py-3">
    <!-- Header -->
    <div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-2 pb-2 border-bottom">
      <div>
        <nav aria-label="breadcrumb">
          <ol class="breadcrumb">
            <li class="breadcrumb-item">
              <router-link to="/admin/dashboard">Admin</router-link>
            </li>
            <li class="breadcrumb-item">
              <router-link to="/admin/parking-lots">Parking Lots</router-link>
            </li>
            <li class="breadcrumb-item active">{{ parkingLot.name }}</li>
          </ol>
        </nav>
        <h1 class="h2 text-primary">{{ parkingLot.name }} - Parking Spots</h1>
      </div>
      <div class="btn-toolbar mb-2 mb-md-0">
        <router-link to="/admin/parking-lots" class="btn btn-sm btn-outline-secondary me-2">
          <i class="fas fa-arrow-left me-1"></i>
          Back to Lots
        </router-link>
        <button class="btn btn-sm btn-outline-primary" @click="refreshSpots">
          <i class="fas fa-sync me-1"></i>
          Refresh
        </button>
      </div>
    </div>

    <!-- Lot Info -->
    <div class="row mt-4">
      <div class="col-12">
        <div class="card shadow-sm">
          <div class="card-body">
            <div class="row">
              <div class="col-md-6">
                <h5>{{ parkingLot.name }}</h5>
                <p class="text-muted">{{ parkingLot.address }}, {{ parkingLot.pin_code }}</p>
              </div>
              <div class="col-md-6 text-md-end">
                <div class="row text-center">
                  <div class="col-3">
                    <div class="text-primary fw-bold fs-4">{{ parkingLot.number_of_spots }}</div>
                    <small class="text-muted">Total</small>
                  </div>
                  <div class="col-3">
                    <div class="text-success fw-bold fs-4">{{ availableCount }}</div>
                    <small class="text-muted">Available</small>
                  </div>
                  <div class="col-3">
                    <div class="text-warning fw-bold fs-4">{{ occupiedCount }}</div>
                    <small class="text-muted">Occupied</small>
                  </div>
                  <div class="col-3">
                    <div class="text-info fw-bold fs-4">{{ reservedCount }}</div>
                    <small class="text-muted">Reserved</small>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Filter and Search -->
    <div class="row mt-4">
      <div class="col-md-6">
        <div class="card">
          <div class="card-body">
            <div class="row align-items-center">
              <div class="col-md-6">
                <label class="form-label">Filter by Status:</label>
                <select class="form-select" v-model="selectedStatus" @change="filterSpots">
                  <option value="">All Spots</option>
                  <option value="A">Available</option>
                  <option value="O">Occupied</option>
                  <option value="R">Reserved</option>
                </select>
              </div>
              <div class="col-md-6">
                <label class="form-label">Search Spot:</label>
                <input 
                  type="text" 
                  class="form-control" 
                  placeholder="Search by spot number"
                  v-model="searchQuery"
                  @input="filterSpots">
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Parking Spots Grid -->
    <div class="row mt-4">
      <div class="col-12">
        <div class="card shadow-sm">
          <div class="card-header">
            <h5 class="mb-0">
              Parking Spots 
              <span class="badge bg-secondary ms-2">{{ filteredSpots.length }} spots</span>
            </h5>
          </div>
          <div class="card-body">
            <div v-if="loading" class="text-center py-4">
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading spots...</span>
              </div>
            </div>
            
            <div v-else-if="spots.length === 0" class="text-center text-muted py-5">
              <i class="fas fa-car fa-4x mb-3"></i>
              <h4>No Parking Spots</h4>
              <p>This parking lot doesn't have any spots yet.</p>
            </div>

            <div v-else class="parking-spots-grid">
              <div 
                v-for="spot in filteredSpots" 
                :key="spot.id"
                class="parking-spot-card"
                :class="{
                  'available': spot.status === 'A',
                  'occupied': spot.status === 'O',
                  'reserved': spot.status === 'R'
                }"
                @click="viewSpotDetails(spot)">
                
                <div class="spot-number">{{ spot.spot_number }}</div>
                <div class="spot-status">
                  <i :class="getSpotIcon(spot.status)"></i>
                  {{ getSpotStatusText(spot.status) }}
                </div>
                
                <div v-if="spot.current_reservation" class="spot-details">
                  <small class="text-muted">
                    <strong>{{ spot.current_reservation.user }}</strong><br>
                    <span v-if="spot.status === 'O'">Since: {{ formatDateTime(spot.current_reservation.check_in_time) }}</span>
                    <span v-if="spot.status === 'R'">Booked: {{ formatDateTime(spot.current_reservation.booking_time) }}</span>
                  </small>
                </div>
              </div>
            </div>

            <!-- Table View for Mobile -->
            <div class="table-responsive d-md-none mt-4">
              <table class="table table-sm">
                <thead>
                  <tr>
                    <th>Spot</th>
                    <th>Status</th>
                    <th>Details</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="spot in filteredSpots" :key="spot.id">
                    <td><strong>{{ spot.spot_number }}</strong></td>
                    <td>
                      <span :class="getSpotBadge(spot.status)">
                        {{ getSpotStatusText(spot.status) }}
                      </span>
                    </td>
                    <td>
                      <span v-if="spot.current_reservation">
                        {{ spot.current_reservation.user }}
                      </span>
                      <span v-else class="text-muted">-</span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Spot Details Modal -->
    <div v-if="selectedSpot" class="modal d-block" tabindex="-1" style="background-color: rgba(0,0,0,0.5)">
      <div class="modal-dialog modal-lg modal-dialog-scrollable">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">
              Spot {{ selectedSpot.spot_number }} Details - {{ parkingLot.name }}
            </h5>
            <button type="button" class="btn-close" @click="closeModal"></button>
          </div>
          <div class="modal-body">
            <!-- Spot Info Card -->
            <div class="card mb-3">
              <div class="card-header">
                <h6 class="mb-0">Spot Information</h6>
              </div>
              <div class="card-body">
                <div class="row">
                  <div class="col-md-6 mb-2">
                    <strong>Status:</strong>
                    <span :class="getSpotBadge(selectedSpot.status) + ' ms-2'">
                      {{ getSpotStatusText(selectedSpot.status) }}
                    </span>
                  </div>
                  <div class="col-md-6 mb-2">
                    <strong>Spot Number:</strong> {{ selectedSpot.spot_number }}
                  </div>
                  <div class="col-12 mb-2">
                    <strong>Parking Lot:</strong> {{ parkingLot.name }}
                  </div>
                  <div class="col-12">
                    <strong>Price Per Hour:</strong> ₹{{ parkingLot.price_per_hour }}/hr
                  </div>
                </div>
              </div>
            </div>
            
            <!-- Current Reservation -->
            <div v-if="selectedSpot.current_reservation" class="card mb-3">
              <div class="card-header">
                <h6 class="mb-0">
                  {{ selectedSpot.status === 'O' ? 'Current Reservation' : 'Pending Reservation' }}
                </h6>
              </div>
              <div class="card-body">
                <table class="table table-sm mb-0">
                  <tbody>
                    <tr>
                      <td><strong>User:</strong></td>
                      <td>{{ selectedSpot.current_reservation.user }}</td>
                    </tr>
                    <tr v-if="selectedSpot.status === 'O'">
                      <td><strong>Check-in Time:</strong></td>
                      <td>{{ formatDateTime(selectedSpot.current_reservation.check_in_time) }}</td>
                    </tr>
                    <tr v-if="selectedSpot.status === 'R'">
                      <td><strong>Booking Time:</strong></td>
                      <td>{{ formatDateTime(selectedSpot.current_reservation.booking_time) }}</td>
                    </tr>
                    <tr>
                      <td><strong>Vehicle Number:</strong></td>
                      <td>{{ selectedSpot.current_reservation.vehicle_number }}</td>
                    </tr>
                    <tr>
                      <td><strong>Status:</strong></td>
                      <td>
                        <span :class="getSpotBadge(selectedSpot.status)">
                          {{ selectedSpot.current_reservation.status }}
                        </span>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
            
            <div v-else class="alert alert-info">
              <i class="fas fa-info-circle me-2"></i>
              This spot is currently available for booking.
            </div>

            <!-- Reservation History -->
            <div class="card">
              <div class="card-header d-flex justify-content-between align-items-center">
                <h6 class="mb-0">Reservation History</h6>
                <span v-if="!loadingHistory" class="badge bg-secondary">
                  {{ spotHistory.length }} records
                </span>
              </div>
              <div class="card-body">
                <div v-if="loadingHistory" class="text-center py-3">
                  <div class="spinner-border spinner-border-sm text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                  </div>
                  <p class="text-muted mt-2 mb-0">Loading history...</p>
                </div>
                
                <div v-else-if="spotHistory.length === 0" class="text-center text-muted py-3">
                  <i class="fas fa-history fa-2x mb-2"></i>
                  <p class="mb-0">No reservation history for this spot.</p>
                </div>
                
                <div v-else class="table-responsive">
                  <table class="table table-sm table-hover mb-0">
                    <thead class="table-light">
                      <tr>
                        <th>User</th>
                        <th>Vehicle</th>
                        <th>Booked</th>
                        <th>Check-in</th>
                        <th>Check-out</th>
                        <th>Status</th>
                        <th>Cost</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="res in spotHistory" :key="res.id">
                        <td>
                          <small>
                            {{ res.user_details ? res.user_details.username : 'N/A' }}
                          </small>
                        </td>
                        <td>
                          <small>{{ res.vehicle_number || 'N/A' }}</small>
                        </td>
                        <td>
                          <small class="text-muted">
                            {{ formatDateTime(res.booking_timestamp) }}
                          </small>
                        </td>
                        <td>
                          <small class="text-muted">
                            {{ res.check_in_timestamp ? formatDateTime(res.check_in_timestamp) : '-' }}
                          </small>
                        </td>
                        <td>
                          <small class="text-muted">
                            {{ res.check_out_timestamp ? formatDateTime(res.check_out_timestamp) : '-' }}
                          </small>
                        </td>
                        <td>
                          <span class="badge" :class="{
                            'bg-warning text-dark': res.status === 'pending',
                            'bg-success': res.status === 'active',
                            'bg-info': res.status === 'completed',
                            'bg-danger': res.status === 'cancelled'
                          }">
                            {{ res.status }}
                          </span>
                        </td>
                        <td>
                          <strong v-if="res.parking_cost">₹{{ res.parking_cost }}</strong>
                          <span v-else class="text-muted">-</span>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="closeModal">Close</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapActions } from 'vuex'

export default {
  name: 'LotSpots',
  data() {
    return {
      loading: true,
      parkingLot: {},
      spots: [],
      filteredSpots: [],
      selectedSpot: null,
      selectedStatus: '',
      searchQuery: '',
      spotHistory: [],
      loadingHistory: false
    }
  },
  
  computed: {
    availableCount() {
      return this.spots.filter(spot => spot.status === 'A').length
    },
    occupiedCount() {
      return this.spots.filter(spot => spot.status === 'O').length
    },
    reservedCount() {
      return this.spots.filter(spot => spot.status === 'R').length
    }
  },
  
  methods: {
    ...mapActions(['setAlert']),
    
    async loadLotSpots() {
      try {
        this.loading = true
        const lotId = this.$route.params.id
        
        const response = await this.$api.admin.getLotSpots(lotId)
        
        this.parkingLot = response.data.lot || {}
        this.spots = response.data.spots || []
        this.filterSpots()
        
      } catch (error) {
        console.error('Error loading lot spots:', error)
        this.setAlert({
          message: 'Failed to load parking spots',
          type: 'error'
        })
        
        if (error.response?.status === 404) {
          this.$router.push('/admin/parking-lots')
        }
      } finally {
        this.loading = false
      }
    },
    
    filterSpots() {
      let filtered = this.spots
      
      if (this.selectedStatus) {
        filtered = filtered.filter(spot => spot.status === this.selectedStatus)
      }
      
      if (this.searchQuery.trim()) {
        filtered = filtered.filter(spot => 
          spot.spot_number.toLowerCase().includes(this.searchQuery.toLowerCase())
        )
      }
      
      this.filteredSpots = filtered
    },
    
    getSpotIcon(status) {
      const icons = {
        'A': 'fas fa-check-circle text-success',
        'O': 'fas fa-car text-warning',
        'R': 'fas fa-clock text-info'
      };
      return icons[status] || 'fas fa-question-circle';
    },

    getSpotStatusText(status) {
      const texts = {
        'A': 'Available',
        'O': 'Occupied',
        'R': 'Reserved'
      };
      return texts[status] || 'Unknown';
    },

    getSpotBadge(status) {
      const badges = {
        'A': 'badge bg-success',
        'O': 'badge bg-warning',
        'R': 'badge bg-info'
      };
      return badges[status] || 'badge bg-secondary';
    },

    async viewSpotDetails(spot) {
      this.selectedSpot = spot
      this.spotHistory = []
      await this.loadSpotHistory(spot.id)
    },
    
    async loadSpotHistory(spotId) {
      try {
        this.loadingHistory = true
        const response = await this.$http.get(`/api/admin/spots/${spotId}/history`)
        this.spotHistory = response.data.history || []
      } catch (error) {
        console.error('Error loading spot history:', error)
        this.setAlert({
          message: 'Failed to load reservation history',
          type: 'error'
        })
      } finally {
        this.loadingHistory = false
      }
    },
    
    closeModal() {
      this.selectedSpot = null
      this.spotHistory = []
      this.loadingHistory = false
    },
    
    async refreshSpots() {
      await this.loadLotSpots()
      this.setAlert({
        message: 'Parking spots refreshed',
        type: 'success'
      })
    },
    
    formatDateTime(dateTime) {
      return this.$formatDateTime(dateTime)
    }
  },
  
  async mounted() {
    await this.loadLotSpots()
  }
}
</script>

<style scoped>
.parking-spots-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 15px;
  margin-top: 20px;
}

.parking-spot-card {
  border: 2px solid #e9ecef;
  border-radius: 8px;
  padding: 15px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.parking-spot-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.parking-spot-card.available {
  border-color: #28a745;
  background-color: #f8fff9;
}

.parking-spot-card.occupied {
  border-color: #ffc107;
  background-color: #fffbf0;
}

.parking-spot-card.reserved {
  border-color: #0dcaf0;
  background-color: #f0fcfd;
}

.spot-number {
  font-size: 1.2rem;
  font-weight: bold;
  margin-bottom: 8px;
}

.spot-status {
  margin-bottom: 10px;
}

.spot-details {
  font-size: 0.8rem;
  border-top: 1px solid #e9ecef;
  padding-top: 8px;
}

@media (max-width: 768px) {
  .parking-spots-grid {
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 10px;
  }
  
  .parking-spot-card {
    padding: 10px;
  }
}
</style>
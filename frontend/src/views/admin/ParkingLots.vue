<template>
  <div class="container-fluid py-3">
    <!-- Header -->
    <div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-2 pb-2 border-bottom">
      <h1 class="h2 text-primary">Manage Parking Lots</h1>
      <div class="btn-toolbar mb-2 mb-md-0">
        <button class="btn btn-sm btn-outline-primary" @click="showCreateModal = true">
          <i class="fas fa-plus-circle me-1"></i>
          Create New Parking Lot
        </button>
      </div>
    </div>

    <!-- Parking Lots List -->
    <div class="card mt-4 shadow-sm">
      <div class="card-header">
        <h5 class="mb-0">All Parking Lots</h5>
      </div>
      <div class="card-body">
        <!-- Search Controls -->
        <div class="row mb-3">
          <div class="col-md-3">
            <label class="form-label">Search By:</label>
            <select class="form-select" v-model="searchType">
              <option value="name">Parking Lot Name</option>
              <option value="location">Location (City/Pin Code)</option>
            </select>
          </div>
          <div class="col-md-9">
            <label class="form-label">Search String:</label>
            <div class="input-group">
              <input
                type="text"
                class="form-control"
                v-model="searchQuery"
                :placeholder="searchType === 'name' ? 'Search by parking lot name...' : 'Search by city or pin code (e.g., Chennai, 600001)...'"
              >
              <button class="btn btn-outline-secondary" @click="clearSearch" v-if="searchQuery">
                <i class="fas fa-times"></i>
              </button>
            </div>
            <small class="text-muted" v-if="searchQuery">
              Showing {{ filteredParkingLots.length }} of {{ parkingLots.length }} parking lots
            </small>
          </div>
        </div>
        
        <div v-if="loading" class="text-center py-4">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
        </div>
        
        <div v-else-if="parkingLots.length === 0" class="text-center text-muted py-5">
          <i class="fas fa-parking fa-4x mb-3"></i>
          <h4>No Parking Lots Found</h4>
          <p>Create your first parking lot to get started.</p>
          <button class="btn btn-primary" @click="showCreateModal = true">
            <i class="fas fa-plus me-2"></i>
            Create Parking Lot
          </button>
        </div>

        <div v-else class="table-responsive">
          <table class="table table-hover">
            <thead class="table-light">
              <tr>
                <th>Name</th>
                <th>Address</th>
                <th>Total Spots</th>
                <th>Available</th>
                <th>Reserved</th>
                <th>Occupied</th>
                <th>Rate/Hour</th>
                <th>Status</th>
                <th class="text-center">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="lot in filteredParkingLots" :key="lot.id">
                <td>
                  <strong>{{ lot.name }}</strong>
                </td>
                <td>{{ lot.address }}, {{ lot.pin_code }}</td>
                <td>
                  <span class="badge text-bg-primary">{{ lot.number_of_spots }}</span>
                </td>
                <td>
                  <span class="badge text-bg-success">{{ lot.available_spots }}</span>
                </td>
                <td>
                  <span class="badge text-bg-info">{{ lot.reserved_spots || 0 }}</span>
                </td>
                <td>
                  <span class="badge text-bg-warning">{{ lot.occupied_spots }}</span>
                </td>
                <td class="text-success fw-bold">₹{{ lot.price_per_hour }}</td>
                <td>
                  <span :class="lot.is_active ? 'badge bg-success' : 'badge bg-danger'">
                    {{ lot.is_active ? 'Active' : 'Inactive' }}
                  </span>
                </td>
                <td class="text-center">
                  <div class="btn-group btn-group-sm" role="group">
                    <button 
                      class="btn btn-outline-secondary"
                      @click="viewLotSpots(lot)"
                      :title="`View ${lot.name} Spots`">
                      <i class="fas fa-eye me-1"></i>View
                    </button>
                    <button 
                      class="btn btn-outline-secondary"
                      @click="editLot(lot)"
                      :title="`Edit ${lot.name}`">
                      <i class="fas fa-edit me-1"></i>Edit
                    </button>
                    <button 
                      class="btn btn-outline-secondary"
                      @click="confirmDeleteLot(lot)"
                      :disabled="lot.occupied_spots > 0 || lot.reserved_spots > 0"
                      :title="(lot.occupied_spots > 0 || lot.reserved_spots > 0) ? 'Cannot delete lot with occupied or reserved spots' : `Delete ${lot.name}`">
                      <i class="fas fa-trash me-1"></i>Delete
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Create/Edit Modal -->
    <div v-if="showCreateModal" class="modal d-block" tabindex="-1" style="background-color: rgba(0,0,0,0.5)">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">
              {{ editingLot ? 'Edit Parking Lot' : 'Create New Parking Lot' }}
            </h5>
            <button type="button" class="btn-close" @click="closeModal"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="saveLot">
              <div class="row">
                <div class="col-md-12 mb-3">
                  <label for="lotName" class="form-label">Lot Name <span class="text-danger">*</span></label>
                  <input 
                    type="text" 
                    class="form-control" 
                    id="lotName" 
                    v-model="lotForm.name"
                    :class="{ 'is-invalid': errors.name }"
                    required>
                  <div v-if="errors.name" class="invalid-feedback">{{ errors.name }}</div>
                </div>
              </div>
              
              <div class="row">
                <div class="col-md-12 mb-3">
                  <label for="address" class="form-label">Address <span class="text-danger">*</span></label>
                  <textarea 
                    class="form-control" 
                    id="address" 
                    v-model="lotForm.address"
                    :class="{ 'is-invalid': errors.address }"
                    rows="2"
                    required></textarea>
                  <div v-if="errors.address" class="invalid-feedback">{{ errors.address }}</div>
                </div>
              </div>
              
              <div class="row">
                <div class="col-md-5 mb-3">
                  <label for="city" class="form-label">City <span class="text-danger">*</span></label>
                  <input 
                    type="text" 
                    class="form-control" 
                    id="city" 
                    v-model="lotForm.city"
                    :class="{ 'is-invalid': errors.city }"
                    placeholder="e.g., Chennai"
                    required>
                  <div v-if="errors.city" class="invalid-feedback">{{ errors.city }}</div>
                </div>
                <div class="col-md-4 mb-3">
                  <label for="state" class="form-label">State</label>
                  <input 
                    type="text" 
                    class="form-control" 
                    id="state" 
                    v-model="lotForm.state"
                    :class="{ 'is-invalid': errors.state }"
                    placeholder="e.g., Tamil Nadu">
                  <div v-if="errors.state" class="invalid-feedback">{{ errors.state }}</div>
                </div>
                <div class="col-md-3 mb-3">
                  <label for="pinCode" class="form-label">Pin Code <span class="text-danger">*</span></label>
                  <input 
                    type="text" 
                    class="form-control" 
                    id="pinCode" 
                    v-model="lotForm.pin_code"
                    :class="{ 'is-invalid': errors.pin_code }"
                    pattern="[0-9]{6}"
                    maxlength="6"
                    required>
                  <div v-if="errors.pin_code" class="invalid-feedback">{{ errors.pin_code }}</div>
                </div>
              </div>
              
              <div class="row">
                <div class="col-md-6 mb-3">
                  <label for="spots" class="form-label">Number of Spots <span class="text-danger">*</span></label>
                  <input 
                    type="number" 
                    class="form-control" 
                    id="spots" 
                    v-model.number="lotForm.number_of_spots"
                    :class="{ 'is-invalid': errors.number_of_spots }"
                    min="1"
                    max="1000"
                    required>
                  <div class="form-text">Spots will be automatically created (A001, A002, etc.)</div>
                  <div v-if="errors.number_of_spots" class="invalid-feedback">{{ errors.number_of_spots }}</div>
                </div>
                <div class="col-md-6 mb-3">
                  <label for="price" class="form-label">Price per Hour ($) <span class="text-danger">*</span></label>
                  <input 
                    type="number" 
                    step="0.01"
                    class="form-control" 
                    id="price" 
                    v-model.number="lotForm.price_per_hour"
                    :class="{ 'is-invalid': errors.price_per_hour }"
                    min="0.01"
                    required>
                  <div v-if="errors.price_per_hour" class="invalid-feedback">{{ errors.price_per_hour }}</div>
                </div>
              </div>
              
              <div class="row">
                <div class="col-12 mb-3">
                  <div class="form-check">
                    <input 
                      class="form-check-input" 
                      type="checkbox" 
                      id="isActive" 
                      v-model="lotForm.is_active">
                    <label class="form-check-label" for="isActive">
                      Active (users can book spots in this lot)
                    </label>
                  </div>
                </div>
              </div>
            </form>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="closeModal">Cancel</button>
            <button type="button" class="btn btn-primary" @click="saveLot" :disabled="saving">
              <span v-if="saving" class="spinner-border spinner-border-sm me-1"></span>
              {{ editingLot ? 'Update Lot' : 'Create Lot' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div v-if="showDeleteModal" class="modal d-block" tabindex="-1" style="background-color: rgba(0,0,0,0.5)">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title text-danger">Confirm Delete</h5>
            <button type="button" class="btn-close" @click="showDeleteModal = false"></button>
          </div>
          <div class="modal-body">
            <p>Are you sure you want to delete the parking lot <strong>"{{ lotToDelete?.name }}"</strong>?</p>
            <p class="text-muted">This action cannot be undone. All parking spots in this lot will be permanently removed.</p>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="showDeleteModal = false">Cancel</button>
            <button type="button" class="btn btn-danger" @click="deleteLot" :disabled="deleting">
              <span v-if="deleting" class="spinner-border spinner-border-sm me-1"></span>
              Delete Lot
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapActions } from 'vuex'

export default {
  name: 'AdminParkingLots',
  data() {
    return {
      loading: true,
      parkingLots: [],
      showCreateModal: false,
      showDeleteModal: false,
      editingLot: null,
      lotToDelete: null,
      saving: false,
      deleting: false,
      searchType: 'name',
      searchQuery: '',
      lotForm: {
        name: '',
        address: '',
        city: '',
        state: '',
        pin_code: '',
        number_of_spots: 10,
        price_per_hour: 5.00,
        is_active: true
      },
      errors: {}
    }
  },
  
  computed: {
    filteredParkingLots() {
      if (!this.searchQuery.trim()) {
        return this.parkingLots
      }
      
      const query = this.searchQuery.toLowerCase().trim()
      
      if (this.searchType === 'name') {
        return this.parkingLots.filter(lot => 
          lot.name.toLowerCase().includes(query)
        )
      } else if (this.searchType === 'location') {
        return this.parkingLots.filter(lot => 
          (lot.city && lot.city.toLowerCase().includes(query)) ||
          (lot.pin_code && lot.pin_code.toLowerCase().includes(query)) ||
          (lot.address && lot.address.toLowerCase().includes(query))
        )
      }
      
      return this.parkingLots
    }
  },
  
  methods: {
    ...mapActions(['setAlert', 'setLoading']),
    
    async loadParkingLots() {
      try {
        this.loading = true
        const response = await this.$api.admin.getParkingLots()
        this.parkingLots = response.data || []
      } catch (error) {
        console.error('Error loading parking lots:', error)
        this.setAlert({
          message: 'Failed to load parking lots',
          type: 'error'
        })
      } finally {
        this.loading = false
      }
    },
    
    editLot(lot) {
      this.editingLot = lot
      this.lotForm = {
        name: lot.name,
        address: lot.address,
        city: lot.city || '',
        state: lot.state || '',
        pin_code: lot.pin_code,
        number_of_spots: lot.number_of_spots,
        price_per_hour: lot.price_per_hour,
        is_active: lot.is_active
      }
      this.showCreateModal = true
    },
    
    confirmDeleteLot(lot) {
      if (lot.occupied_spots > 0 || lot.reserved_spots > 0) {
        this.setAlert({
          message: 'Cannot delete parking lot with occupied or reserved spots. Please wait for all spots to be available.',
          type: 'error'
        })
        return
      }
      this.lotToDelete = lot
      this.showDeleteModal = true
    },
    
    async deleteLot() {
      try {
        this.deleting = true
        await this.$api.admin.deleteParkingLot(this.lotToDelete.id)
        
        this.setAlert({
          message: `Parking lot "${this.lotToDelete.name}" deleted successfully`,
          type: 'success'
        })
        
        this.showDeleteModal = false
        this.lotToDelete = null
        await this.loadParkingLots()
        
      } catch (error) {
        console.error('Error deleting parking lot:', error)
        this.setAlert({
          message: error.response?.data?.error || 'Failed to delete parking lot',
          type: 'error'
        })
      } finally {
        this.deleting = false
      }
    },
    
    async saveLot() {
      try {
        this.saving = true
        this.errors = {}
        
        if (this.editingLot) {
          // Update existing lot
          await this.$api.admin.updateParkingLot(this.editingLot.id, this.lotForm)
          this.setAlert({
            message: 'Parking lot updated successfully',
            type: 'success'
          })
        } else {
          // Create new lot
          await this.$api.admin.createParkingLot(this.lotForm)
          this.setAlert({
            message: 'Parking lot created successfully',
            type: 'success'
          })
        }
        
        this.closeModal()
        await this.loadParkingLots()
        
      } catch (error) {
        console.error('Error saving parking lot:', error)
        
        if (error.response?.status === 400 && error.response?.data?.errors) {
          this.errors = error.response.data.errors
        } else {
          this.setAlert({
            message: error.response?.data?.error || 'Failed to save parking lot',
            type: 'error'
          })
        }
      } finally {
        this.saving = false
      }
    },
    
    viewLotSpots(lot) {
      // Navigate to lot spots view
      this.$router.push(`/admin/parking-lots/${lot.id}/spots`)
    },
    
    closeModal() {
      this.showCreateModal = false
      this.editingLot = null
      this.lotForm = {
        name: '',
        address: '',
        city: '',
        state: '',
        pin_code: '',
        number_of_spots: 10,
        price_per_hour: 5.00,
        is_active: true
      }
      this.errors = {}
    },
    
    clearSearch() {
      this.searchQuery = ''
    }
  },
  
  watch: {
    '$route.query': {
      immediate: true,
      handler(query) {
        if (query.search && query.type) {
          this.searchQuery = query.search
          this.searchType = query.type === 'location' ? 'location' : 'name'
        }
      }
    }
  },
  
  async mounted() {
    await this.loadParkingLots()
  }
}
</script>

<style scoped>
/* Lighter badge styles for better number visibility */
.text-bg-primary {
  background-color: rgba(13, 110, 253, 0.15) !important;
  color: #0d6efd !important;
  border: 1px solid #0d6efd;
  font-weight: 600;
  padding: 0.35em 0.65em;
  display: inline-block;
  min-width: 2.5rem;
  text-align: center;
}

.text-bg-success {
  background-color: rgba(25, 135, 84, 0.15) !important;
  color: #198754 !important;
  border: 1px solid #198754;
  font-weight: 600;
  padding: 0.35em 0.65em;
  display: inline-block;
  min-width: 2.5rem;
  text-align: center;
}

.text-bg-info {
  background-color: rgba(13, 202, 240, 0.15) !important;
  color: #0dcaf0 !important;
  border: 1px solid #0dcaf0;
  font-weight: 600;
  padding: 0.35em 0.65em;
  display: inline-block;
  min-width: 2.5rem;
  text-align: center;
}

.text-bg-warning {
  background-color: rgba(255, 193, 7, 0.15) !important;
  color: #ff8c00 !important;
  border: 1px solid #ffc107;
  font-weight: 600;
  padding: 0.35em 0.65em;
  display: inline-block;
  min-width: 2.5rem;
  text-align: center;
}

/* Table cell alignment */
.table td {
  vertical-align: middle;
}

/* Action buttons styling */
.btn-group-sm > .btn {
  white-space: nowrap;
}
</style>
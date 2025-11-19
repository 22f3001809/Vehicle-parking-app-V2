<template>
  <div class="container-fluid py-4">
    <!-- Header -->
    <div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-2 pb-2 border-bottom">
      <div>
        <h1 class="h2 text-primary">User Management</h1>
        <p class="text-muted">Manage system users and their permissions</p>
      </div>
    </div>

    <!-- Users List -->
    <div class="card mt-4 shadow-sm">
      <div class="card-header">
        <h5 class="mb-0">All Users</h5>
      </div>
      <div class="card-body">
        <div v-if="loading" class="text-center py-4">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
        </div>
        
        <div v-else-if="users.length === 0" class="text-center text-muted py-5">
          <i class="fas fa-users fa-4x mb-3"></i>
          <h4>No Users Found</h4>
          <p>There are no users registered in the system yet.</p>
        </div>

        <div v-else class="table-responsive">
          <table class="table table-hover">
            <thead class="table-light">
              <tr>
                <th>ID</th>
                <th>Full Name</th>
                <th>Username</th>
                <th>Email</th>
                <th>Role</th>
                <th>Status</th>
                <th>Last Login</th>
                <th>Registered</th>
                <th>Reservations</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="user in users" :key="user.id">
                <td>
                  <span class="badge bg-secondary">{{ user.id }}</span>
                </td>
                <td>
                  <strong>{{ user.full_name }}</strong>
                </td>
                <td>
                  <code>{{ user.username }}</code>
                </td>
                <td>{{ user.email }}</td>
                <td>
                  <span :class="user.is_admin ? 'badge bg-danger' : 'badge bg-primary'">
                    {{ user.is_admin ? 'Admin' : 'User' }}
                  </span>
                </td>
                <td>
                  <span :class="user.is_active ? 'badge bg-success' : 'badge bg-danger'">
                    {{ user.is_active ? 'Active' : 'Inactive' }}
                  </span>
                </td>
                <td>
                  <small class="text-muted">
                    {{ user.last_login ? formatDate(user.last_login) : 'Never' }}
                  </small>
                </td>
                <td>
                  <small class="text-muted">
                    {{ formatDate(user.created_at) }}
                  </small>
                </td>
                <td class="text-center">
                  <button 
                    class="btn btn-sm btn-outline-secondary"
                    @click="viewUserDetails(user)">
                    {{ user.reservation_count || 0 }}
                    <i class="fas fa-eye ms-1"></i>
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- User Details Modal -->
    <div v-if="selectedUser" class="modal show d-block" tabindex="-1" style="background-color: rgba(0,0,0,0.5);">
      <div class="modal-dialog modal-lg modal-dialog-scrollable">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">
              <i class="fas fa-user-circle me-2"></i>
              {{ selectedUser.full_name || selectedUser.username }}
            </h5>
            <button type="button" class="btn-close" @click="selectedUser = null"></button>
          </div>
          <div class="modal-body">
            <div v-if="loadingDetails" class="text-center py-4">
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
            </div>
            <div v-else>
              <!-- User Info -->
              <div class="card mb-3">
                <div class="card-header">
                  <h6 class="mb-0">User Information</h6>
                </div>
                <div class="card-body">
                  <div class="row">
                    <div class="col-md-6 mb-2">
                      <strong>Username:</strong> {{ selectedUser.username }}
                    </div>
                    <div class="col-md-6 mb-2">
                      <strong>Email:</strong> {{ selectedUser.email }}
                    </div>
                    <div class="col-md-6 mb-2">
                      <strong>Phone:</strong> {{ selectedUser.phone_number || 'N/A' }}
                    </div>
                    <div class="col-md-6 mb-2">
                      <strong>Status:</strong>
                      <span :class="selectedUser.is_active ? 'badge bg-success' : 'badge bg-danger'">
                        {{ selectedUser.is_active ? 'Active' : 'Inactive' }}
                      </span>
                    </div>
                    <div class="col-md-6 mb-2">
                      <strong>Joined:</strong> {{ formatDate(selectedUser.created_at) }}
                    </div>
                    <div class="col-md-6 mb-2">
                      <strong>Last Login:</strong> {{ selectedUser.last_login ? formatDate(selectedUser.last_login) : 'Never' }}
                    </div>
                  </div>
                </div>
              </div>

              <!-- Reservations -->
              <div class="card">
                <div class="card-header">
                  <h6 class="mb-0">Reservation History ({{ userReservations.length }})</h6>
                </div>
                <div class="card-body">
                  <div v-if="userReservations.length === 0" class="text-center text-muted py-3">
                    <i class="fas fa-calendar-times fa-2x mb-2"></i>
                    <p class="mb-0">No reservations yet</p>
                  </div>
                  <div v-else class="table-responsive">
                    <table class="table table-sm">
                      <thead>
                        <tr>
                          <th>ID</th>
                          <th>Vehicle</th>
                          <th>Spot</th>
                          <th>Check-in</th>
                          <th>Check-out</th>
                          <th>Cost</th>
                          <th>Status</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr v-for="res in userReservations" :key="res.id">
                          <td>{{ res.id }}</td>
                          <td>{{ res.vehicle_number }}</td>
                          <td>{{ res.spot_number || 'N/A' }}</td>
                          <td><small>{{ res.check_in_timestamp ? formatDateTime(res.check_in_timestamp) : '-' }}</small></td>
                          <td><small>{{ res.check_out_timestamp ? formatDateTime(res.check_out_timestamp) : '-' }}</small></td>
                          <td>₹{{ res.parking_cost || '0.00' }}</td>
                          <td>
                            <span class="badge" :class="{
                              'bg-warning': res.status === 'pending',
                              'bg-success': res.status === 'active',
                              'bg-info': res.status === 'completed',
                              'bg-danger': res.status === 'cancelled'
                            }">
                              {{ res.status }}
                            </span>
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="selectedUser = null">Close</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapActions } from 'vuex'

export default {
  name: 'AdminUsers',
  data() {
    return {
      users: [],
      loading: true,
      selectedUser: null,
      userReservations: [],
      loadingDetails: false
    }
  },
  methods: {
    ...mapActions(['setAlert']),
    
    async loadUsers() {
      try {
        this.loading = true
        const response = await this.$api.admin.getAllUsers()
        this.users = response.data || []
      } catch (error) {
        console.error('Error loading users:', error)
        this.setAlert({
          message: 'Failed to load users',
          type: 'error'
        })
      } finally {
        this.loading = false
      }
    },
    
    async viewUserDetails(user) {
      this.selectedUser = user
      this.loadingDetails = true
      this.userReservations = []
      
      try {
        // Fetch user details with reservations
        const response = await this.$api.admin.getUserDetails(user.id)
        this.userReservations = response.data.reservations || []
      } catch (error) {
        console.error('Error loading user details:', error)
        this.setAlert({
          message: 'Failed to load user details',
          type: 'error'
        })
      } finally {
        this.loadingDetails = false
      }
    },
    
    formatDate(dateString) {
      if (!dateString) return 'N/A'
      return new Date(dateString).toLocaleDateString()
    },
    
    formatDateTime(dateString) {
      return this.$formatDateTime(dateString)
    }
  },
  
  async mounted() {
    await this.loadUsers()
  }
}
</script>

<style scoped>
/* Table styling */
.table td {
  vertical-align: middle;
}

.table th {
  font-weight: 700;
  font-size: 0.875rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: #212529;
}

/* Badge styling - minimal and clean */
.badge {
  font-weight: 500;
  padding: 0.35em 0.65em;
  font-size: 0.875rem;
}

/* Code styling for username */
code {
  background-color: #f8f9fa;
  padding: 0.2rem 0.4rem;
  border-radius: 0.25rem;
  color: #495057;
  font-size: 0.875rem;
}

/* Button in reservations column */
.btn-outline-secondary {
  border-color: #dee2e6;
}

.btn-outline-secondary:hover {
  background-color: #f8f9fa;
  border-color: #adb5bd;
  color: #495057;
}

/* Small text styling */
small.text-muted {
  font-size: 0.875rem;
}

/* Modal improvements */
.modal-content {
  border: none;
  box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
}

.modal-header {
  background-color: #f8f9fa;
  border-bottom: 1px solid #dee2e6;
}

.card {
  border: 1px solid #e3e6f0;
}

.card-header {
  background-color: #f8f9fa;
  border-bottom: 1px solid #e3e6f0;
  font-weight: 600;
}
</style>
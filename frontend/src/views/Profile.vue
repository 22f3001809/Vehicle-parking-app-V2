<template>
  <div class="container-fluid py-4">
    <div class="row">
      <div class="col-12">
        <div class="card shadow-sm">
          <div class="card-header text-white" :class="user?.is_admin ? 'bg-primary' : 'bg-success'">
            <h4 class="mb-0">
              <i class="fas fa-user-circle me-2"></i>
              {{ user?.is_admin ? 'Admin Profile' : 'Edit Profile' }}
            </h4>
          </div>
          <div class="card-body">
            <form @submit.prevent="updateProfile">
              <div class="row">
                <div class="col-md-6 mb-3">
                  <label for="username" class="form-label">Username</label>
                  <input type="text" 
                         class="form-control" 
                         id="username" 
                         v-model="profile.username" 
                         readonly>
                </div>
                <div class="col-md-6 mb-3">
                  <label for="email" class="form-label">Email</label>
                  <input type="email" 
                         class="form-control" 
                         id="email" 
                         v-model="profile.email" 
                         required>
                </div>
              </div>
              <div class="row">
                <div class="col-md-6 mb-3">
                  <label for="firstName" class="form-label">First Name</label>
                  <input type="text" 
                         class="form-control" 
                         id="firstName" 
                         v-model="profile.firstName">
                </div>
                <div class="col-md-6 mb-3">
                  <label for="lastName" class="form-label">Last Name</label>
                  <input type="text" 
                         class="form-control" 
                         id="lastName" 
                         v-model="profile.lastName">
                </div>
              </div>
              <div class="row">
                <div class="col-md-6 mb-3">
                  <label for="address" class="form-label">Address</label>
                  <input type="text" 
                         class="form-control" 
                         id="address" 
                         v-model="profile.address">
                </div>
                <div class="col-md-6 mb-3">
                  <label for="pincode" class="form-label">Pin Code</label>
                  <input type="text" 
                         class="form-control" 
                         id="pincode" 
                         v-model="profile.pincode">
                </div>
              </div>
              <div class="row">
                <div class="col-md-6 mb-3">
                  <label for="phone" class="form-label">Phone Number</label>
                  <input type="tel" 
                         class="form-control" 
                         id="phone" 
                         v-model="profile.phone">
                </div>
                <div class="col-md-6 mb-3">
                  <label for="vehicleNumber" class="form-label">Vehicle Number</label>
                  <input type="text" 
                         class="form-control" 
                         id="vehicleNumber" 
                         v-model="profile.vehicleNumber" 
                         placeholder="ABC-1234">
                </div>
              </div>
              <div class="row mt-4">
                <div class="col-12">
                  <button type="submit" 
                          class="btn btn-primary me-3" 
                          :disabled="loading">
                    <i class="fas fa-save me-2"></i>
                    {{ loading ? 'Updating...' : 'Update Profile' }}
                  </button>
                  <button type="button" 
                          class="btn btn-outline-secondary" 
                          @click="showChangePassword = !showChangePassword">
                    <i class="fas fa-key me-2"></i>
                    Change Password
                  </button>
                </div>
              </div>
            </form>

            <div v-if="showChangePassword" class="mt-4 pt-4 border-top">
              <h5>Change Password</h5>
              <form @submit.prevent="changePassword">
                <div class="row">
                  <div class="col-md-4 mb-3">
                    <label for="currentPassword" class="form-label">Current Password</label>
                    <input type="password" 
                           class="form-control" 
                           id="currentPassword" 
                           v-model="passwordForm.currentPassword" 
                           required>
                  </div>
                  <div class="col-md-4 mb-3">
                    <label for="newPassword" class="form-label">New Password</label>
                    <input type="password" 
                           class="form-control" 
                           id="newPassword" 
                           v-model="passwordForm.newPassword" 
                           required>
                  </div>
                  <div class="col-md-4 mb-3">
                    <label for="confirmPassword" class="form-label">Confirm Password</label>
                    <input type="password" 
                           class="form-control" 
                           id="confirmPassword" 
                           v-model="passwordForm.confirmPassword" 
                           required>
                  </div>
                </div>
                <button type="submit" 
                        class="btn btn-warning" 
                        :disabled="passwordLoading">
                  <i class="fas fa-key me-2"></i>
                  {{ passwordLoading ? 'Changing...' : 'Change Password' }}
                </button>
              </form>
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
  name: 'Profile',
  data() {
    return {
      profile: {
        username: '',
        email: '',
        firstName: '',
        lastName: '',
        address: '', 
        pincode: '', 
        phone: '',
        vehicleNumber: ''
      },
      passwordForm: {
        currentPassword: '',
        newPassword: '',
        confirmPassword: ''
      },
      showChangePassword: false,
      loading: false,
      passwordLoading: false
    }
  },
  computed: {
    ...mapState('auth', ['user'])
  },
  methods: {
    ...mapActions(['setAlert']),
    async updateProfile() {
      this.loading = true
      
      const fullName = `${this.profile.firstName} ${this.profile.lastName}`.trim()

      try {
        const response = await this.$api.user.updateProfile({
          full_name: fullName,
          email: this.profile.email,
          phone_number: this.profile.phone,
          address: this.profile.address, 
          pincode: this.profile.pincode, 
          vehicle_number: this.profile.vehicleNumber 
        })
        
        // Update user in store with the new data
        this.$store.commit('auth/SET_USER', response.data.user)
        
        this.setAlert({
          message: 'Profile updated successfully!',
          type: 'success'
        })
      } catch (error) {
        console.error('Profile update error:', error)
        this.setAlert({
          message: error.response?.data?.error || 'Failed to update profile',
          type: 'error'
        })
      } finally {
        this.loading = false
      }
    },
    async changePassword() {
      if (this.passwordForm.newPassword !== this.passwordForm.confirmPassword) {
        this.setAlert({
          message: 'Passwords do not match',
          type: 'error'
        })
        return
      }
      
      if (this.passwordForm.newPassword.length < 6) {
        this.setAlert({
          message: 'New password must be at least 6 characters',
          type: 'error'
        })
        return
      }
      
      this.passwordLoading = true
      try {
        await this.$api.user.changePassword({
          current_password: this.passwordForm.currentPassword,
          new_password: this.passwordForm.newPassword
        })
        
        this.setAlert({
          message: 'Password changed successfully!',
          type: 'success'
        })
        
        this.passwordForm = {
          currentPassword: '',
          newPassword: '',
          confirmPassword: ''
        }
        this.showChangePassword = false
      } catch (error) {
        console.error('Password change error:', error)
        this.setAlert({
          message: error.response?.data?.error || 'Failed to change password',
          type: 'error'
        })
      } finally {
        this.passwordLoading = false
      }
    },
    loadProfile() {
      if (this.user) {
        const nameParts = (this.user.full_name || '').trim().split(/\s+/)
        const firstName = nameParts[0] || ''
        const lastName = nameParts.length > 1 ? nameParts.slice(1).join(' ') : ''
        
        this.profile = {
          username: this.user.username || '',
          email: this.user.email || '',
          firstName: firstName,
          lastName: lastName,
          address: this.user.address || '', 
          pincode: this.user.pin_code || '', 
          phone: this.user.phone_number || '',
          vehicleNumber: this.user.vehicle_number || ''
        }
      }
    }
  },
  mounted() {
    this.loadProfile()
  },
  watch: {
    user: {
      handler: 'loadProfile',
      immediate: true 
    }
  }
}
</script>

<style scoped>
.form-control:read-only {
  background-color: #f8f9fa;
}

.border-top {
  border-color: #e3e6f0 !important;
}
</style>
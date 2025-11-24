<template>
  <div class="register-page">
    <div class="container">
      <div class="row justify-content-center align-items-center min-vh-100">
        <div class="col-md-6 col-lg-5">
          <div class="card shadow">
            <div class="card-header bg-success text-white text-center py-4">
              <h3 class="mb-0">
                Create Account
              </h3>
              <p class="mb-0 mt-2 opacity-75">Join our parking community</p>
            </div>
            
            <div class="card-body p-4">
              <form @submit.prevent="handleRegister">
                <!-- Full Name -->
                <div class="mb-3">
                  <label for="fullName" class="form-label">
                    Full Name
                  </label>
                  <input
                    type="text"
                    class="form-control form-control-lg"
                    id="fullName"
                    v-model="form.full_name"
                    :class="{ 'is-invalid': errors.full_name }"
                    placeholder="Enter your full name"
                    required
                  >
                  <div v-if="errors.full_name" class="invalid-feedback">
                    {{ errors.full_name }}
                  </div>
                </div>

                <!-- Username -->
                <div class="mb-3">
                  <label for="username" class="form-label">
                    Username
                  </label>
                  <input
                    type="text"
                    class="form-control form-control-lg"
                    id="username"
                    v-model="form.username"
                    :class="{ 'is-invalid': errors.username }"
                    placeholder="Choose a unique username"
                    required
                  >
                  <div v-if="errors.username" class="invalid-feedback">
                    {{ errors.username }}
                  </div>
                  <div class="form-text">
                    Username must be unique and contain only letters, numbers, and underscores.
                  </div>
                </div>

                <!-- Email -->
                <div class="mb-3">
                  <label for="email" class="form-label">
                    Email Address
                  </label>
                  <input
                    type="email"
                    class="form-control form-control-lg"
                    id="email"
                    v-model="form.email"
                    :class="{ 'is-invalid': errors.email }"
                    placeholder="Enter your email address"
                    required
                  >
                  <div v-if="errors.email" class="invalid-feedback">
                    {{ errors.email }}
                  </div>
                </div>

                <!-- Address -->
                <div class="mb-3">
                  <label for="address" class="form-label">
                    Address
                  </label>
                  <textarea
                    class="form-control form-control-lg"
                    id="address"
                    v-model="form.address"
                    :class="{ 'is-invalid': errors.address }"
                    placeholder="Enter your full address"
                    rows="2"
                    required
                  ></textarea>
                  <div v-if="errors.address" class="invalid-feedback">
                    {{ errors.address }}
                  </div>
                </div>

                <!-- Pin Code -->
                <div class="mb-3">
                  <label for="pinCode" class="form-label">
                    Pin Code
                  </label>
                  <input
                    type="text"
                    class="form-control form-control-lg"
                    id="pinCode"
                    v-model="form.pin_code"
                    :class="{ 'is-invalid': errors.pin_code }"
                    placeholder="Enter your pin code"
                    pattern="[0-9]{6}"
                    maxlength="6"
                    required
                  >
                  <div v-if="errors.pin_code" class="invalid-feedback">
                    {{ errors.pin_code }}
                  </div>
                  <div class="form-text">
                    6-digit pin code
                  </div>
                </div>

                <!-- Password -->
                <div class="mb-3">
                  <label for="password" class="form-label">
                    Password
                  </label>
                  <div class="input-group">
                    <input
                      :type="showPassword ? 'text' : 'password'"
                      class="form-control form-control-lg"
                      id="password"
                      v-model="form.password"
                      :class="{ 'is-invalid': errors.password }"
                      placeholder="Create a strong password"
                      required
                    >
                    <button
                      type="button"
                      class="btn btn-outline-secondary"
                      @click="showPassword = !showPassword"
                    >
                      <i :class="showPassword ? 'bi bi-eye-slash' : 'bi bi-eye'"></i>
                    </button>
                  </div>
                  <div v-if="errors.password" class="invalid-feedback d-block">
                    {{ errors.password }}
                  </div>
                  <div class="form-text">
                    Password must be at least 6 characters long.
                  </div>
                </div>

                <!-- Confirm Password -->
                <div class="mb-3">
                  <label for="confirmPassword" class="form-label">
                    Confirm Password
                  </label>
                  <div class="input-group">
                    <input
                      :type="showConfirmPassword ? 'text' : 'password'"
                      class="form-control form-control-lg"
                      id="confirmPassword"
                      v-model="form.confirmPassword"
                      :class="{ 'is-invalid': errors.confirmPassword }"
                      placeholder="Confirm your password"
                      required
                    >
                    <button
                      type="button"
                      class="btn btn-outline-secondary"
                      @click="showConfirmPassword = !showConfirmPassword"
                    >
                      <i :class="showConfirmPassword ? 'bi bi-eye-slash' : 'bi bi-eye'"></i>
                    </button>
                  </div>
                  <div v-if="errors.confirmPassword" class="invalid-feedback d-block">
                    {{ errors.confirmPassword }}
                  </div>
                </div>

                <!-- Terms Agreement -->
                <div class="mb-3 form-check">
                  <input
                    type="checkbox"
                    class="form-check-input"
                    id="agreeTerms"
                    v-model="form.agreeTerms"
                    :class="{ 'is-invalid': errors.agreeTerms }"
                    required
                  >
                  <label class="form-check-label" for="agreeTerms">
                    I agree to the Terms of Service and Privacy Policy
                  </label>
                  <div v-if="errors.agreeTerms" class="invalid-feedback d-block">
                    {{ errors.agreeTerms }}
                  </div>
                </div>

                <!-- Submit Button -->
                <button
                  type="submit"
                  class="btn btn-success btn-lg w-100 mb-3"
                  :disabled="loading"
                  :class="{ 'btn-loading': loading }"
                >
                  <span v-if="loading">
                    <span class="spinner-border spinner-border-sm me-2" role="status"></span>
                    Creating Account...
                  </span>
                  <span v-else>
                    Create Account
                  </span>
                </button>
              </form>
            </div>
            
            <div class="card-footer text-center py-3 bg-light">
              <p class="mb-0">
                Already have an account?
                <router-link to="/login" class="text-decoration-none">
                  Sign in here
                </router-link>
              </p>
            </div>
          </div>
          
          <!-- Back to Home -->
          <div class="text-center mt-3">
            <router-link to="/" class="text-muted text-decoration-none">
              Back to Home
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapState } from 'vuex'

export default {
  name: 'Register',
  data() {
    return {
      form: {
        full_name: '',
        username: '',
        email: '',
        address: '',
        pin_code: '',
        password: '',
        confirmPassword: '',
        agreeTerms: false
      },
      errors: {},
      showPassword: false,
      showConfirmPassword: false
    }
  },
  computed: {
    loading() {
      return this.$store.getters['auth/registerLoading'] || this.$store.getters.loading
    }
  },
  methods: {
    validateForm() {
      this.errors = {}
      let isValid = true

      // Full name validation
      if (!this.form.full_name.trim()) {
        this.errors.full_name = 'Full name is required'
        isValid = false
      } else if (this.form.full_name.trim().length < 2) {
        this.errors.full_name = 'Full name must be at least 2 characters'
        isValid = false
      }

      // Username validation
      if (!this.form.username.trim()) {
        this.errors.username = 'Username is required'
        isValid = false
      } else if (this.form.username.length < 3) {
        this.errors.username = 'Username must be at least 3 characters'
        isValid = false
      } else if (!/^[a-zA-Z0-9_]+$/.test(this.form.username)) {
        this.errors.username = 'Username can only contain letters, numbers, and underscores'
        isValid = false
      }

      // Email validation
      if (!this.form.email.trim()) {
        this.errors.email = 'Email is required'
        isValid = false
      } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(this.form.email)) {
        this.errors.email = 'Please enter a valid email address'
        isValid = false
      }

      // Address validation
      if (!this.form.address.trim()) {
        this.errors.address = 'Address is required'
        isValid = false
      } else if (this.form.address.trim().length < 10) {
        this.errors.address = 'Address must be at least 10 characters'
        isValid = false
      }

      // Pin code validation
      if (!this.form.pin_code.trim()) {
        this.errors.pin_code = 'Pin code is required'
        isValid = false
      } else if (!/^[0-9]{6}$/.test(this.form.pin_code)) {
        this.errors.pin_code = 'Pin code must be 6 digits'
        isValid = false
      }

      // Password validation
      if (!this.form.password) {
        this.errors.password = 'Password is required'
        isValid = false
      } else if (this.form.password.length < 6) {
        this.errors.password = 'Password must be at least 6 characters'
        isValid = false
      }

      // Confirm password validation
      if (!this.form.confirmPassword) {
        this.errors.confirmPassword = 'Please confirm your password'
        isValid = false
      } else if (this.form.password !== this.form.confirmPassword) {
        this.errors.confirmPassword = 'Passwords do not match'
        isValid = false
      }

      // Terms agreement validation
      if (!this.form.agreeTerms) {
        this.errors.agreeTerms = 'You must agree to the terms and conditions'
        isValid = false
      }

      return isValid
    },

    async handleRegister() {
      if (!this.validateForm()) {
        return
      }

      try {
        const result = await this.$store.dispatch('auth/register', {
          full_name: this.form.full_name.trim(),
          username: this.form.username.trim().toLowerCase(),
          email: this.form.email.trim().toLowerCase(),
          address: this.form.address.trim(),
          pin_code: this.form.pin_code.trim(),
          password: this.form.password
        })
        
        if (result.success) {
          // Registration successful, automatically logged in, redirect based on role
          const user = result.user
          if (user.is_admin) {
            this.$router.push('/admin/dashboard')
          } else {
            this.$router.push('/user/dashboard')
          }
        } else {
          this.$store.dispatch('setAlert', {
            message: result.message || 'Registration failed',
            type: 'error'
          })
        }
      } catch (error) {
        console.error('Registration error:', error)
        
        // Handle specific server errors
        if (error.response?.data?.error) {
          const errorMessage = error.response.data.error
          
          if (errorMessage.toLowerCase().includes('username')) {
            this.errors.username = errorMessage
          } else if (errorMessage.toLowerCase().includes('email')) {
            this.errors.email = errorMessage
          } else {
            this.$store.dispatch('setAlert', {
              message: errorMessage,
              type: 'error'
            })
          }
        } else {
          this.$store.dispatch('setAlert', {
            message: 'Registration failed. Please try again.',
            type: 'error'
          })
        }
      }
    }
  },
  created() {
    // Clear any existing alerts
    this.$store.dispatch('clearAlert')
  }
}
</script>

<style scoped>
.register-page {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  min-height: 100vh;
}

.card {
  border: none;
  border-radius: 15px;
  overflow: hidden;
}

.card-header {
  background: linear-gradient(135deg, #28a745 0%, #1e7e34 100%) !important;
  border: none;
}

.form-control-lg {
  border-radius: 10px;
  border: 2px solid #e9ecef;
  transition: all 0.3s ease;
}

.form-control-lg:focus {
  border-color: #28a745;
  box-shadow: 0 0 0 0.2rem rgba(40, 167, 69, 0.25);
}

.btn-success {
  border-radius: 10px;
  border: none;
  background: linear-gradient(135deg, #28a745 0%, #1e7e34 100%);
  transition: all 0.3s ease;
}

.btn-success:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(40, 167, 69, 0.3);
}

.btn-loading {
  position: relative;
}

/* Animation for form elements */
.form-control, .btn {
  transition: all 0.3s ease;
}

/* Form validation styles */
.is-invalid {
  border-color: #dc3545;
}

.form-check-input.is-invalid {
  border-color: #dc3545;
}

@media (max-width: 576px) {
  .container {
    padding: 1rem;
  }
  
  .card {
    margin: 1rem 0;
  }
}
</style>
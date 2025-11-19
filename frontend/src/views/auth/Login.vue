<template>
  <div class="login-page">
    <div class="container">
      <div class="row justify-content-center align-items-center min-vh-100">
        <div class="col-md-6 col-lg-5">
          <div class="card shadow">
            <div class="card-header bg-primary text-white text-center py-4">
              <h3 class="mb-0">
                <i class="bi bi-car-front-fill me-2"></i>
                Sign In
              </h3>
              <p class="mb-0 mt-2 opacity-75">Access your parking account</p>
            </div>
            
            <div class="card-body p-4">
              <form @submit.prevent="handleLogin">
                <!-- Username -->
                <div class="mb-3">
                  <label for="username" class="form-label">
                    <i class="bi bi-person-fill me-1"></i>
                    Username
                  </label>
                  <input
                    type="text"
                    class="form-control form-control-lg"
                    id="username"
                    v-model="form.username"
                    :class="{ 'is-invalid': errors.username }"
                    placeholder="Enter your username"
                    required
                  >
                  <div v-if="errors.username" class="invalid-feedback">
                    {{ errors.username }}
                  </div>
                </div>

                <!-- Password -->
                <div class="mb-3">
                  <label for="password" class="form-label">
                    <i class="bi bi-lock-fill me-1"></i>
                    Password
                  </label>
                  <div class="input-group">
                    <input
                      :type="showPassword ? 'text' : 'password'"
                      class="form-control form-control-lg"
                      id="password"
                      v-model="form.password"
                      :class="{ 'is-invalid': errors.password }"
                      placeholder="Enter your password"
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
                </div>

                <!-- Remember Me -->
                <div class="mb-3 form-check">
                  <input
                    type="checkbox"
                    class="form-check-input"
                    id="rememberMe"
                    v-model="form.rememberMe"
                  >
                  <label class="form-check-label" for="rememberMe">
                    Remember me
                  </label>
                </div>

                <!-- Submit Button -->
                <button
                  type="submit"
                  class="btn btn-primary btn-lg w-100 mb-3"
                  :disabled="loading"
                  :class="{ 'btn-loading': loading }"
                >
                  <span v-if="loading">
                    <span class="spinner-border spinner-border-sm me-2" role="status"></span>
                    Signing In...
                  </span>
                  <span v-else>
                    <i class="bi bi-box-arrow-in-right me-2"></i>
                    Sign In
                  </span>
                </button>
              </form>
            </div>
            
            <div class="card-footer text-center py-3 bg-light">
              <p class="mb-0">
                Don't have an account?
                <router-link to="/register" class="text-decoration-none">
                  <i class="bi bi-person-plus me-1"></i>
                  Register here
                </router-link>
              </p>
            </div>
          </div>
          
          <!-- Back to Home -->
          <div class="text-center mt-3">
            <router-link to="/" class="text-muted text-decoration-none">
              <i class="bi bi-arrow-left me-1"></i>
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
  name: 'Login',
  data() {
    return {
      form: {
        username: '',
        password: '',
        rememberMe: false
      },
      errors: {},
      showPassword: false
    }
  },
  computed: {
    loading() {
      return this.$store.getters['auth/loginLoading'] || this.$store.getters.loading
    }
  },
  methods: {
    async handleLogin() {
      // Clear previous errors
      this.errors = {}
      
      // Basic validation
      if (!this.form.username.trim()) {
        this.errors.username = 'Username is required'
        return
      }
      
      if (!this.form.password) {
        this.errors.password = 'Password is required'
        return
      }

      try {
        const result = await this.$store.dispatch('auth/login', {
          username: this.form.username.trim(),
          password: this.form.password
        })
        
        if (result.success) {
          // Redirect based on user role
          const user = result.user
          if (user.is_admin) {
            this.$router.push('/admin/dashboard')
          } else {
            this.$router.push('/user/dashboard')
          }
        } else {
          this.errors.password = result.message || 'Login failed'
        }
      } catch (error) {
        console.error('Login error:', error)
        
        // Handle specific error cases
        if (error.response?.status === 401) {
          this.errors.password = 'Invalid username or password'
        } else {
          this.$store.dispatch('setAlert', {
            message: 'Login failed. Please try again.',
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
.login-page {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  min-height: 100vh;
}

.card {
  border: none;
  border-radius: 15px;
  overflow: hidden;
}

.card-header {
  background: linear-gradient(135deg, #007bff 0%, #0056b3 100%) !important;
  border: none;
}

.form-control-lg {
  border-radius: 10px;
  border: 2px solid #e9ecef;
  transition: all 0.3s ease;
}

.form-control-lg:focus {
  border-color: #007bff;
  box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25);
}

.btn-primary {
  border-radius: 10px;
  border: none;
  background: linear-gradient(135deg, #007bff 0%, #0056b3 100%);
  transition: all 0.3s ease;
}

.btn-primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 123, 255, 0.3);
}

.btn-loading {
  position: relative;
}

.alert {
  border-radius: 10px;
  border: none;
}

/* Animation for form elements */
.form-control, .btn {
  transition: all 0.3s ease;
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
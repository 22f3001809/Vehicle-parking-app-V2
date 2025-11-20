<template>
  <div class="home-page">
    <!-- Hero Section -->
    <section class="hero">
      <div class="container">
        <div class="row">
          <!-- Left/Center Side - Main Content -->
          <div class="col-lg-7">
            <div class="hero-content">
              <!-- Brand Logo -->
              <h1 class="brand-title">
                <span class="brand-park">Park</span><span class="brand-nxt">Nxt</span>
              </h1>
              
              <!-- Main Heading -->
              <h2 class="main-heading">
                Your seamless solution for smart parking management.
              </h2>
              
              <!-- Tagline -->
              <p class="tagline">
                Find, book, and park effortlessly.
              </p>
              
              <!-- CTA Buttons -->
              <div class="cta-buttons">
                <button 
                  @click="authMode = 'login'" 
                  class="btn btn-primary btn-lg px-4 me-3">
                  Login
                </button>
                <button 
                  @click="authMode = 'register'" 
                  class="btn btn-outline-primary btn-lg px-4">
                  Register
                </button>
              </div>
            </div>
          </div>
          
          <!-- Right Side - Auth Forms -->
          <div class="col-lg-5">
            <div class="auth-card" v-if="authMode">
              <!-- Login Form -->
              <form v-if="authMode === 'login'" @submit.prevent="handleLogin" class="auth-form">
                <h3 class="form-title">Welcome Back</h3>
                <div class="mb-3">
                  <label class="form-label">Username</label>
                  <input 
                    v-model="loginForm.username" 
                    type="text" 
                    class="form-control" 
                    required
                    placeholder="Enter your username">
                </div>
                <div class="mb-3">
                  <label class="form-label">Password</label>
                  <input 
                    v-model="loginForm.password" 
                    type="password" 
                    class="form-control" 
                    required
                    placeholder="Enter your password">
                </div>
                <button type="submit" class="btn btn-primary w-100" :disabled="loggingIn">
                  <span v-if="loggingIn" class="spinner-border spinner-border-sm me-2"></span>
                  {{ loggingIn ? 'Logging in...' : 'Login' }}
                </button>
                <p class="switch-mode">
                  Don't have an account? 
                  <a href="#" @click.prevent="authMode = 'register'">Register</a>
                </p>
              </form>

              <!-- Register Form -->
              <form v-if="authMode === 'register'" @submit.prevent="handleRegister" class="auth-form">
                <h3 class="form-title">Create Account</h3>
                <div class="mb-3">
                  <label class="form-label">Full Name</label>
                  <input 
                    v-model="registerForm.full_name" 
                    type="text" 
                    class="form-control" 
                    required
                    placeholder="Enter your full name">
                </div>
                <div class="mb-3">
                  <label class="form-label">Username</label>
                  <input 
                    v-model="registerForm.username" 
                    type="text" 
                    class="form-control" 
                    required
                    placeholder="Choose a username">
                </div>
                <div class="mb-3">
                  <label class="form-label">Email</label>
                  <input 
                    v-model="registerForm.email" 
                    type="email" 
                    class="form-control" 
                    required
                    placeholder="Enter your email">
                </div>
                <div class="mb-3">
                  <label class="form-label">Password</label>
                  <input 
                    v-model="registerForm.password" 
                    type="password" 
                    class="form-control" 
                    required
                    placeholder="Create a password">
                </div>
                <div class="mb-3">
                  <label class="form-label">Confirm Password</label>
                  <input 
                    v-model="registerForm.confirm_password" 
                    type="password" 
                    class="form-control" 
                    required
                    placeholder="Confirm your password">
                </div>
                <button type="submit" class="btn btn-primary w-100" :disabled="registering">
                  <span v-if="registering" class="spinner-border spinner-border-sm me-2"></span>
                  {{ registering ? 'Creating Account...' : 'Register' }}
                </button>
                <p class="switch-mode">
                  Already have an account? 
                  <a href="#" @click.prevent="authMode = 'login'">Login</a>
                </p>
              </form>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Features Section -->
    <section class="features-section">
      <div class="container">
        <h2 class="section-title">Key Features</h2>
        
        <div class="row g-4">
          <div class="col-md-6">
            <div class="feature-card">
              <div class="feature-icon">
                <i class="bi bi-geo-alt"></i>
              </div>
              <h5 class="feature-title">Easy Spot Finding</h5>
              <p class="feature-description">Locate available parking spots in real-time.</p>
            </div>
          </div>
          
          <div class="col-md-6">
            <div class="feature-card">
              <div class="feature-icon">
                <i class="bi bi-calendar-check"></i>
              </div>
              <h5 class="feature-title">Hassle-Free Booking</h5>
              <p class="feature-description">Reserve your spot in advance with a few clicks.</p>
            </div>
          </div>
        </div>
      </div>
    </section>

  </div>
</template>

<script>
import { mapGetters, mapActions } from 'vuex'

export default {
  name: 'Home',
  data() {
    return {
      authMode: 'login', // 'login' or 'register'
      loginForm: {
        username: '',
        password: ''
      },
      registerForm: {
        full_name: '',
        username: '',
        email: '',
        password: '',
        confirm_password: ''
      },
      loggingIn: false,
      registering: false
    }
  },
  computed: {
    ...mapGetters(['isAuthenticated', 'isAdmin'])
  },
  methods: {
    ...mapActions(['setAlert']),
    
    async handleLogin() {
      this.loggingIn = true
      try {
        const result = await this.$store.dispatch('auth/login', this.loginForm)
        
        if (result.success) {
          // Redirect based on user role
          if (result.user.is_admin) {
            this.$router.push('/admin/dashboard')
          } else {
            this.$router.push('/user/dashboard')
          }
        }
      } catch (error) {
        console.error('Login error:', error)
      } finally {
        this.loggingIn = false
      }
    },
    
    async handleRegister() {
      // Validate password match
      if (this.registerForm.password !== this.registerForm.confirm_password) {
        this.setAlert({
          message: 'Passwords do not match',
          type: 'error'
        })
        return
      }
      
      this.registering = true
      try {
        // Remove confirm_password before sending to backend
        const { confirm_password, ...registerData } = this.registerForm
        
        const result = await this.$store.dispatch('auth/register', registerData)
        
        if (result.success) {
          // Redirect to user dashboard (new users are not admins)
          this.$router.push('/user/dashboard')
        }
      } catch (error) {
        console.error('Register error:', error)
      } finally {
        this.registering = false
      }
    }
  },
  
  // Redirect if already authenticated
  created() {
    if (this.isAuthenticated) {
      if (this.isAdmin) {
        this.$router.push('/admin/dashboard')
      } else {
        this.$router.push('/user/dashboard')
      }
    }
  }
}
</script>

<style scoped>
.home-page {
  background-color: #ffffff;
  min-height: 100vh;
}

/* Hero Section */
.hero {
  background-color: #f8f9fa;
  padding: 80px 0;
  min-height: 85vh;
  display: flex;
  align-items: center;
}

.hero-content {
  padding: 40px 0;
}

/* Brand Title */
.brand-title {
  font-size: 3rem;
  font-weight: 700;
  margin-bottom: 2rem;
}

.brand-park {
  color: #000000;
}

.brand-nxt {
  color: #4285f4;
}

/* Main Heading */
.main-heading {
  font-size: 2rem;
  font-weight: 400;
  color: #5f6368;
  margin-bottom: 1.5rem;
  line-height: 1.5;
}

/* Tagline */
.tagline {
  font-size: 1.1rem;
  color: #5f6368;
  margin-bottom: 2.5rem;
}

/* CTA Buttons */
.cta-buttons {
  margin-top: 2rem;
}

.cta-buttons .btn {
  border-radius: 4px;
  font-weight: 500;
  padding: 12px 32px;
}

.cta-buttons .btn-primary {
  background-color: #4285f4;
  border-color: #4285f4;
}

.cta-buttons .btn-primary:hover {
  background-color: #3367d6;
  border-color: #3367d6;
}

.cta-buttons .btn-outline-primary {
  color: #4285f4;
  border-color: #4285f4;
}

.cta-buttons .btn-outline-primary:hover {
  background-color: #4285f4;
  color: #ffffff;
}

/* Auth Card */
.auth-card {
  background-color: #ffffff;
  border: 1px solid #dadce0;
  border-radius: 8px;
  padding: 40px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.12);
  margin-top: 20px;
}

.auth-form {
  width: 100%;
}

.form-title {
  font-size: 1.5rem;
  font-weight: 500;
  color: #202124;
  margin-bottom: 1.5rem;
  text-align: center;
}

.auth-card .form-label {
  font-weight: 500;
  font-size: 0.875rem;
  color: #5f6368;
  margin-bottom: 0.5rem;
}

.auth-card .form-control {
  padding: 12px 16px;
  border: 1px solid #dadce0;
  border-radius: 4px;
  font-size: 0.875rem;
}

.auth-card .form-control:focus {
  border-color: #4285f4;
  box-shadow: 0 0 0 0.2rem rgba(66, 133, 244, 0.15);
}

.auth-card .btn-primary {
  background-color: #4285f4;
  border-color: #4285f4;
  padding: 12px;
  font-weight: 500;
  margin-top: 0.5rem;
}

.auth-card .btn-primary:hover {
  background-color: #3367d6;
  border-color: #3367d6;
}

.switch-mode {
  text-align: center;
  margin-top: 1.5rem;
  font-size: 0.875rem;
  color: #5f6368;
}

.switch-mode a {
  color: #4285f4;
  text-decoration: none;
  font-weight: 500;
}

.switch-mode a:hover {
  text-decoration: underline;
}

/* Features Section */
.features-section {
  background-color: #ffffff;
  padding: 80px 0;
}

.section-title {
  text-align: center;
  font-size: 2rem;
  font-weight: 500;
  color: #4285f4;
  margin-bottom: 3rem;
}

.feature-card {
  text-align: center;
  padding: 40px 20px;
  background-color: #f8f9fa;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.feature-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.feature-icon {
  margin-bottom: 1.5rem;
}

.feature-icon i {
  font-size: 3rem;
  color: #4285f4;
}

.feature-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #4285f4;
  margin-bottom: 1rem;
}

.feature-description {
  font-size: 1rem;
  color: #5f6368;
  margin: 0;
}

/* Responsive Design */
@media (max-width: 992px) {
  .hero {
    padding: 60px 0;
  }
  
  .hero-content {
    text-align: center;
    margin-bottom: 40px;
  }
  
  .brand-title {
    font-size: 2.5rem;
  }
  
  .main-heading {
    font-size: 1.5rem;
  }
  
  .cta-buttons {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }
  
  .cta-buttons .btn {
    width: 100%;
    margin: 0 !important;
  }
  
  .auth-card {
    margin-top: 0;
  }
}

@media (max-width: 768px) {
  .brand-title {
    font-size: 2rem;
  }
  
  .main-heading {
    font-size: 1.25rem;
  }
  
  .auth-card {
    padding: 30px 20px;
  }
}
</style>
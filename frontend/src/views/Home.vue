<template>
  <div class="home-page">
    <section class="hero">
      <div class="container">
        <div class="row">
          <div class="col-lg-7">
            <div class="hero-content">
              <h1 class="brand-title">
                <span class="brand-park">Park</span><span class="brand-nxt">Nxt</span>
              </h1>
              
              <h2 class="main-heading">
                Your seamless solution for smart parking management.
              </h2>
              
              <p class="tagline">
                Find, book, and park effortlessly.
              </p>
              
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
          
          <div class="col-lg-5">
            <div class="auth-card" v-if="authMode">
              <Login v-if="authMode === 'login'" @switch-mode="switchAuthMode" />
              <Register v-if="authMode === 'register'" @switch-mode="switchAuthMode" />
            </div>
          </div>
        </div>
      </div>
    </section>

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
import { mapGetters } from 'vuex'
import Login from './auth/Login.vue'
import Register from './auth/Register.vue'

export default {
  name: 'Home',
  components: {
    Login,
    Register
  },
  data() {
    return {
      authMode: 'login' // 'login' or 'register'
    }
  },
  computed: {
    ...mapGetters(['isAuthenticated', 'isAdmin'])
  },
  methods: {
    switchAuthMode(mode) {
      this.authMode = mode
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

.main-heading {
  font-size: 2rem;
  font-weight: 400;
  color: #5f6368;
  margin-bottom: 1.5rem;
  line-height: 1.5;
}

.tagline {
  font-size: 1.1rem;
  color: #5f6368;
  margin-bottom: 2.5rem;
}

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
.auth-card {
  background-color: #ffffff;
  border: 1px solid #dadce0;
  border-radius: 8px;
  padding: 40px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.12);
  margin-top: -20px;
}



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
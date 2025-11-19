<template>
  <div class="home-page">
    <!-- Hero Section -->
    <section class="hero bg-primary text-white py-5">
      <div class="container">
        <div class="row align-items-center">
          <div class="col-lg-6">
            <h1 class="display-4 fw-bold mb-4">
              <i class="bi bi-car-front-fill"></i>
              Smart Parking Solutions
            </h1>
            <p class="lead mb-4">
              Find, book, and manage parking spots effortlessly with our modern parking management system.
            </p>
            <div class="d-flex flex-wrap gap-3">
              <router-link v-if="!isAuthenticated" to="/register" class="btn btn-light btn-lg">
                Get Started
              </router-link>
              <router-link v-if="isAuthenticated && !isAdmin" to="/user/dashboard" class="btn btn-light btn-lg">
                Go to Dashboard
              </router-link>
              <router-link v-if="isAuthenticated && isAdmin" to="/admin/dashboard" class="btn btn-light btn-lg">
                Admin Dashboard
              </router-link>
            </div>
          </div>
          <div class="col-lg-6 text-center">
            <i class="bi bi-p-square-fill" style="font-size: 12rem; opacity: 0.3;"></i>
          </div>
        </div>
      </div>
    </section>

    <!-- Features Section -->
    <section class="features py-5">
      <div class="container">
        <div class="row text-center mb-5">
          <div class="col">
            <h2 class="fw-bold">Why Choose Our Parking System?</h2>
            <p class="text-muted">Modern features for seamless parking management</p>
          </div>
        </div>
        
        <div class="row g-4">
          <div class="col-md-4">
            <div class="card h-100 border-0 shadow-sm">
              <div class="card-body text-center p-4">
                <i class="bi bi-search text-primary" style="font-size: 3rem;"></i>
                <h5 class="card-title mt-3">Easy Search</h5>
                <p class="card-text">Find available parking spots near your location with real-time availability.</p>
              </div>
            </div>
          </div>
          
          <div class="col-md-4">
            <div class="card h-100 border-0 shadow-sm">
              <div class="card-body text-center p-4">
                <i class="bi bi-calendar-check text-success" style="font-size: 3rem;"></i>
                <h5 class="card-title mt-3">Quick Booking</h5>
                <p class="card-text">Book parking spots instantly with automatic allocation and confirmation.</p>
              </div>
            </div>
          </div>
          
          <div class="col-md-4">
            <div class="card h-100 border-0 shadow-sm">
              <div class="card-body text-center p-4">
                <i class="bi bi-shield-check text-info" style="font-size: 3rem;"></i>
                <h5 class="card-title mt-3">Secure & Reliable</h5>
                <p class="card-text">Advanced security features with reliable payment processing and data protection.</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Call to Action (light theme only) -->
    <section class="cta bg-light text-dark py-5" v-if="!isAuthenticated">
      <div class="container text-center">
        <div class="row">
          <div class="col-lg-8 mx-auto">
            <h2 class="fw-bold mb-4">Ready to Get Started?</h2>
            <p class="lead mb-4">
              Join thousands of users who trust our parking management system.
            </p>
            <div class="d-flex justify-content-center gap-3">
              <router-link to="/register" class="btn btn-primary btn-lg">
                Register Now
              </router-link>
              <router-link to="/login" class="btn btn-outline-secondary btn-lg">
                Sign In
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script>
import { mapGetters } from 'vuex'

export default {
  name: 'Home',
  computed: {
    ...mapGetters(['isAuthenticated', 'isAdmin'])
  }
}
</script>

<style scoped>
.hero {
  background: linear-gradient(135deg, #007bff 0%, #0056b3 100%);
}

.features .card {
  transition: transform 0.3s ease;
}

.features .card:hover {
  transform: translateY(-5px);
}

.statistics .card {
  transition: all 0.3s ease;
}

.statistics .card:hover {
  transform: scale(1.05);
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .hero {
    text-align: center;
  }
  
  .hero .display-4 {
    font-size: 2.5rem;
  }
  
  .hero i[style*="font-size: 12rem"] {
    font-size: 6rem !important;
  }
}
</style>
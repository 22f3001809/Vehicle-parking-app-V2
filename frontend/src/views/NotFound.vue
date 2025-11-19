<template>
  <div class="not-found-page">
    <div class="container">
      <div class="row justify-content-center align-items-center min-vh-100">
        <div class="col-md-6 text-center">
          <div class="error-content">
            <i class="bi bi-exclamation-triangle-fill text-warning" style="font-size: 6rem;"></i>
            <h1 class="display-1 fw-bold text-primary">404</h1>
            <h2 class="mb-4">Page Not Found</h2>
            <p class="lead text-muted mb-4">
              Sorry, the page you are looking for doesn't exist or has been moved.
            </p>
            <div class="d-flex justify-content-center gap-3 flex-wrap">
              <router-link to="/" class="btn btn-primary btn-lg">
                <i class="bi bi-house-fill me-2"></i>
                Go Home
              </router-link>
              <button @click="$router.go(-1)" class="btn btn-outline-secondary btn-lg">
                <i class="bi bi-arrow-left me-2"></i>
                Go Back
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'NotFound'
}
</script>

<style scoped>
.not-found-page {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  min-height: 100vh;
}

.error-content {
  animation: fadeInUp 0.6s ease-out;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.display-1 {
  font-size: 8rem;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
}

@media (max-width: 576px) {
  .display-1 {
    font-size: 4rem;
  }
  
  .bi-exclamation-triangle-fill {
    font-size: 3rem !important;
  }
}
</style>
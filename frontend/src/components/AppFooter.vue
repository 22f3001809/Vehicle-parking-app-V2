<template>
  <footer class="footer">
    <div class="container">
      <div class="row align-items-center">
        <div class="col-md-6">
          <p class="mb-0">
            <span class="logo-primary">Park</span><span class="logo-secondary">Nxt</span>
          </p>
        </div>
        <div class="col-md-6 text-md-end">
          <p class="mb-0 text-muted">
            &copy; {{ currentYear }} ParkNxt. All rights reserved.
          </p>
        </div>
      </div>
    </div>
  </footer>
</template>

<script>
export default {
  name: 'AppFooter',
  computed: {
    currentYear() {
      return new Date().getFullYear()
    }
  }
}
</script>

<style scoped>
.row {
  display: flex;
  flex-wrap: wrap;
  margin-right: -0.75rem;
  margin-left: -0.75rem;
}

.col-md-6 {
  flex: 0 0 auto;
  width: 50%;
  padding-right: 0.75rem;
  padding-left: 0.75rem;
}

.align-items-center {
  align-items: center !important;
}

.mb-0 {
  margin-bottom: 0 !important;
}

.ms-2 {
  margin-left: 0.5rem !important;
}

@media (max-width: 768px) {
  .col-md-6 {
    width: 100%;
    text-align: center !important;
    margin-bottom: var(--spacing-sm);
  }
  
  .text-md-end {
    text-align: center !important;
  }
}
</style>

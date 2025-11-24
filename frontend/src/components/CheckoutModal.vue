<template>
  <div class="modal fade" id="checkoutModal" tabindex="-1" aria-labelledby="checkoutModalLabel" aria-hidden="true">
    <div class="modal-dialog modal-dialog-centered modal-lg">
      <div class="modal-content">
        <div class="modal-header bg-warning text-dark">
          <h5 class="modal-title" id="checkoutModalLabel">
            <i class="fas fa-sign-out-alt me-2"></i>Release the Parking Spot
          </h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
        </div>
        <div class="modal-body">
          <p class="mb-4">Please review the parking details before checking out:</p>
          
          <div class="row g-3">
            <!-- Spot ID -->
            <div class="col-md-6">
              <div class="detail-card">
                <label class="detail-label">Spot ID</label>
                <div class="detail-value">
                  <i class="fas fa-parking me-2 text-primary"></i>
                  {{ details.spot_id || 'N/A' }}
                </div>
              </div>
            </div>
            
            <!-- Vehicle Number -->
            <div class="col-md-6">
              <div class="detail-card">
                <label class="detail-label">Vehicle Number</label>
                <div class="detail-value">
                  <i class="fas fa-car me-2 text-primary"></i>
                  {{ details.vehicle_number || 'N/A' }}
                </div>
              </div>
            </div>
            
            <!-- Parking Time (Check-in) -->
            <div class="col-md-6">
              <div class="detail-card">
                <label class="detail-label">Parking Time</label>
                <div class="detail-value">
                  <i class="fas fa-clock me-2 text-success"></i>
                  {{ details.check_in_time || 'N/A' }}
                </div>
              </div>
            </div>
            
            <!-- Releasing Time (Check-out) -->
            <div class="col-md-6">
              <div class="detail-card">
                <label class="detail-label">Releasing Time</label>
                <div class="detail-value">
                  <i class="fas fa-clock me-2 text-danger"></i>
                  {{ details.check_out_time || 'Now' }}
                </div>
              </div>
            </div>
            
            <!-- Duration -->
            <div class="col-md-6">
              <div class="detail-card">
                <label class="detail-label">Parking Duration</label>
                <div class="detail-value">
                  <i class="fas fa-hourglass-half me-2 text-info"></i>
                  {{ details.duration || 'N/A' }}
                </div>
              </div>
            </div>
            
            <!-- Total Cost -->
            <div class="col-md-6">
              <div class="detail-card highlight-card">
                <label class="detail-label">Total Cost</label>
                <div class="detail-value text-success fw-bold fs-4">
                  <i class="fas fa-rupee-sign me-2"></i>
                  ₹{{ details.cost || '0.00' }}
                </div>
              </div>
            </div>
          </div>
          
          <div class="alert alert-info mt-4 mb-0">
            <i class="fas fa-info-circle me-2"></i>
            <small>This amount will be charged upon confirmation. Please proceed to payment counter.</small>
          </div>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
            <i class="fas fa-times me-2"></i>Cancel
          </button>
          <button type="button" class="btn btn-primary" @click="confirmCheckout">
            <i class="fas fa-check me-2"></i>Release & Confirm
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CheckoutModal',
  props: {
    details: {
      type: Object,
      required: true,
      default: () => ({ 
        spot_id: null,
        vehicle_number: null,
        check_in_time: null,
        check_out_time: null,
        duration: 'N/A',
        cost: 0 
      })
    }
  },
  methods: {
    confirmCheckout() {
      this.$emit('confirmed');
    }
  }
}
</script>

<style scoped>
.detail-card {
  background-color: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  padding: 1rem;
  height: 100%;
  transition: all 0.3s ease;
}

.detail-card:hover {
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.highlight-card {
  background-color: #d4edda;
  border-color: #c3e6cb;
}

.detail-label {
  display: block;
  font-size: 0.875rem;
  color: #6c757d;
  margin-bottom: 0.5rem;
  font-weight: 500;
}

.detail-value {
  font-size: 1rem;
  color: #212529;
  font-weight: 600;
  display: flex;
  align-items: center;
}

.modal-lg {
  max-width: 700px;
}
</style>

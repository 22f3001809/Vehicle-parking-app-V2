<template>
  <div class="modal fade" id="checkoutModal" tabindex="-1" aria-labelledby="checkoutModalLabel" aria-hidden="true">
    <div class="modal-dialog modal-dialog-centered">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title" id="checkoutModalLabel">Confirm Checkout</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
        </div>
        <div class="modal-body">
          <p>Please confirm the details before checking out:</p>
          <ul class="list-group">
            <li class="list-group-item d-flex justify-content-between align-items-center">
              Parking Duration
              <strong>{{ details.duration }}</strong>
            </li>
            <li class="list-group-item d-flex justify-content-between align-items-center">
              Estimated Cost
              <strong>₹{{ details.cost }}</strong>
            </li>
          </ul>
          <p class="mt-3 text-muted">This amount will be charged upon confirmation.</p>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
          <button type="button" class="btn btn-primary" @click="confirmCheckout">Confirm & Check Out</button>
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
      default: () => ({ cost: 0, duration: 'N/A' })
    }
  },
  methods: {
    confirmCheckout() {
      this.$emit('confirmed');
    }
  }
}
</script>

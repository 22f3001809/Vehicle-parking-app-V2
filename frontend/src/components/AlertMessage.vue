<template>
  <div class="container mt-3" v-if="message">
    <div 
      :class="['alert', 'alert-dismissible', 'fade', 'show', alertClass]"
      role="alert"
    >
      <i :class="[alertIcon, 'me-2']"></i>
      {{ message }}
      <button 
        type="button" 
        class="btn-close" 
        @click="handleClose" 
        aria-label="Close"
      ></button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AlertMessage',
  props: {
    message: {
      type: String,
      default: ''
    },
    type: {
      type: String,
      default: 'info',
      validator: (value) => ['error', 'success', 'warning', 'info'].includes(value)
    }
  },
  computed: {
    alertClass() {
      const classes = {
        error: 'alert-danger',
        success: 'alert-success',
        warning: 'alert-warning',
        info: 'alert-info'
      }
      return classes[this.type] || 'alert-info'
    },
    alertIcon() {
      const icons = {
        error: 'fas fa-exclamation-circle',
        success: 'fas fa-check-circle',
        warning: 'fas fa-exclamation-triangle',
        info: 'fas fa-info-circle'
      }
      return icons[this.type] || 'fas fa-info-circle'
    }
  },
  methods: {
    handleClose() {
      this.$emit('close')
    }
  }
}
</script>

<style scoped>
.container {
  width: 100%;
  padding-right: var(--spacing-lg);
  padding-left: var(--spacing-lg);
  margin-right: auto;
  margin-left: auto;
}

.mt-3 {
  margin-top: 1rem !important;
}

.me-2 {
  margin-right: 0.5rem !important;
}

.fade {
  transition: opacity var(--transition-fast);
}

.show {
  opacity: 1;
}
</style>

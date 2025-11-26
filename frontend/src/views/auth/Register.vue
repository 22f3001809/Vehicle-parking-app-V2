<template>
  <form @submit.prevent="handleRegister" class="auth-form">
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
      <a href="#" @click.prevent="$emit('switch-mode', 'login')">Login</a>
    </p>
  </form>
</template>

<script>
import { mapActions } from 'vuex'

export default {
  name: 'Register',
  emits: ['switch-mode'],
  data() {
    return {
      registerForm: {
        full_name: '',
        username: '',
        email: '',
        password: '',
        confirm_password: ''
      },
      registering: false
    }
  },
  methods: {
    ...mapActions(['setAlert']),
    
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
  }
}
</script>

<style scoped>
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

.form-label {
  font-weight: 500;
  font-size: 0.875rem;
  color: #5f6368;
  margin-bottom: 0.5rem;
}

.form-control {
  padding: 12px 16px;
  border: 1px solid #dadce0;
  border-radius: 4px;
  font-size: 0.875rem;
}

.form-control:focus {
  border-color: #4285f4;
  box-shadow: 0 0 0 0.2rem rgba(66, 133, 244, 0.15);
}

.btn-primary {
  background-color: #4285f4;
  border-color: #4285f4;
  padding: 12px;
  font-weight: 500;
  margin-top: 0.5rem;
}

.btn-primary:hover {
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
</style>

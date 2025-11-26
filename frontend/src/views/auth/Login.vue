<template>
  <form @submit.prevent="handleLogin" class="auth-form">
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
      {{ loggingIn ? 'Logging in...' : 'LET ME IN!' }}
    </button>
    <p class="switch-mode">
      Don't have an account? 
      <a href="#" @click.prevent="$emit('switch-mode', 'register')">Register</a>
    </p>
  </form>
</template>

<script>
import { mapActions } from 'vuex'

export default {
  name: 'Login',
  emits: ['switch-mode'],
  data() {
    return {
      loginForm: {
        username: '',
        password: ''
      },
      loggingIn: false
    }
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

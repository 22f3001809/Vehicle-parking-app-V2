<template>
  <div id="app">
    <!-- Navigation Bar -->
    <NavBar />

    <!-- Main Content -->
    <main class="main-content">
      <!-- Loading Overlay -->
      <LoadingOverlay :is-loading="loading" />
      
      <!-- Alert Messages -->
      <AlertMessage 
        :message="alertMessage" 
        :type="alertType" 
        @close="clearAlert" 
      />
      
      <!-- Router View -->
      <div class="container-fluid">
        <router-view />
      </div>
    </main>

    <!-- Footer -->
    <AppFooter />
  </div>
</template>

<script>
import { mapGetters, mapActions } from 'vuex'
import NavBar from './components/NavBar.vue'
import AppFooter from './components/AppFooter.vue'
import AlertMessage from './components/AlertMessage.vue'
import LoadingOverlay from './components/LoadingOverlay.vue'

export default {
  name: 'App',
  components: {
    NavBar,
    AppFooter,
    AlertMessage,
    LoadingOverlay
  },
  computed: {
    ...mapGetters(['loading', 'alertMessage', 'alertType'])
  },
  methods: {
    ...mapActions(['clearAlert'])
  },
  async created() {
    // Check if user is already logged in
    const token = localStorage.getItem('access_token')
    if (token) {
      try {
        // Set the token first
        this.$store.commit('auth/SET_TOKEN', { 
          access_token: token, 
          refresh_token: localStorage.getItem('refresh_token') 
        })
        
        // Then fetch current user
        await this.$store.dispatch('auth/fetchCurrentUser')
      } catch (error) {
        // Token might be expired, clear it
        this.$store.commit('auth/LOGOUT')
      }
    }
  }
}
</script>

<style scoped>
/* Minimal App-specific styles - most styles are now in global CSS */
.container-fluid {
  width: 100%;
  padding-right: var(--spacing-lg);
  padding-left: var(--spacing-lg);
  margin-right: auto;
  margin-left: auto;
}
</style>
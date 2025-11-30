<template>
  <div id="app">
    <NavBar />

    <main class="main-content">
      <LoadingOverlay :is-loading="loading" />
      <AlertMessage 
        :message="alertMessage" 
        :type="alertType" 
        @close="clearAlert" 
      />
      <div class="container-fluid">
        <router-view />
      </div>
    </main>
  </div>
</template>

<script>
import { mapGetters, mapActions } from 'vuex'
import NavBar from './components/NavBar.vue'
import AlertMessage from './components/AlertMessage.vue'
import LoadingOverlay from './components/LoadingOverlay.vue'

export default {
  name: 'App',
  components: {
    NavBar,
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
.container-fluid {
  width: 100%;
  padding-right: var(--spacing-lg);
  padding-left: var(--spacing-lg);
  margin-right: auto;
  margin-left: auto;
}
</style>
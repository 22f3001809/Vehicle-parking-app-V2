<template>
  <nav class="navbar navbar-expand-lg">
    <div class="container">
      <!-- Logo/Brand -->
      <router-link :to="homeLink" class="navbar-brand navbar-logo">
        <span class="logo-primary">Park</span><span class="logo-secondary">Nxt</span>
      </router-link>
      
      <!-- Mobile Toggle Button -->
      <button 
        class="navbar-toggler" 
        type="button" 
        @click="toggleMobileMenu"
        aria-label="Toggle navigation"
      >
        <i class="fas fa-bars"></i>
      </button>
      
      <!-- Navigation Menu -->
      <div class="navbar-collapse" :class="{ show: isMobileMenuOpen }">
        <ul class="navbar-nav me-auto">
          <!-- Authenticated User Links -->
          <template v-if="isAuthenticated">
            <!-- Admin Links -->
            <template v-if="user?.is_admin">
              <li class="nav-item">
                <router-link to="/admin/parking-lots" class="nav-link" @click="closeMobileMenu">
                  <i class="fas fa-parking me-1"></i>
                  Manage Lots
                </router-link>
              </li>
              <li class="nav-item">
                <router-link to="/admin/users" class="nav-link" @click="closeMobileMenu">
                  <i class="fas fa-users me-1"></i>
                  View Users
                </router-link>
              </li>
              <li class="nav-item">
                <router-link to="/admin/reports" class="nav-link" @click="closeMobileMenu">
                  <i class="fas fa-chart-bar me-1"></i>
                  Reports
                </router-link>
              </li>
            </template>
            
            <!-- Regular User Links -->
            <template v-else>
              <li class="nav-item">
                <router-link to="/parking-lots" class="nav-link" @click="closeMobileMenu">
                  <i class="fas fa-search me-1"></i>
                  Book Parking
                </router-link>
              </li>
              <li class="nav-item">
                <router-link to="/user/reservations" class="nav-link" @click="closeMobileMenu">
                  <i class="fas fa-calendar me-1"></i>
                  My Reservations
                </router-link>
              </li>
            </template>
          </template>
        </ul>
        
        <!-- Right Side Navigation -->
        <ul class="navbar-nav">
          <!-- User Dropdown when authenticated -->
          <li v-if="isAuthenticated" class="nav-item dropdown">
            <a 
              class="nav-link dropdown-toggle" 
              href="#" 
              @click.prevent="toggleDropdown"
              role="button"
            >
              <i class="fas fa-user-circle me-1"></i>
              {{ user?.username || user?.full_name || 'User' }}
            </a>
            <ul class="dropdown-menu" :class="{ show: isDropdownOpen }">
              <li>
                <router-link 
                  :to="user?.is_admin ? '/admin/dashboard' : '/user/dashboard'" 
                  class="dropdown-item"
                  @click="closeDropdown"
                >
                  <i class="fas fa-tachometer-alt me-2"></i>
                  Dashboard
                </router-link>
              </li>
              <li v-if="!user?.is_admin">
                <router-link to="/profile" class="dropdown-item" @click="closeDropdown">
                  <i class="fas fa-user-edit me-2"></i>
                  Profile
                </router-link>
              </li>
              <li>
                <hr class="dropdown-divider">
              </li>
              <li>
                <button @click="handleLogout" class="dropdown-item text-danger">
                  <i class="fas fa-sign-out-alt me-2"></i>
                  Logout
                </button>
              </li>
            </ul>
          </li>
          
          <!-- Login/Register when not authenticated -->
          <template v-else>
            <li class="nav-item">
              <router-link to="/login" class="nav-link" @click="closeMobileMenu">
                <i class="fas fa-sign-in-alt me-1"></i>
                Login
              </router-link>
            </li>
            <li class="nav-item">
              <router-link to="/register" class="nav-link" @click="closeMobileMenu">
                <i class="fas fa-user-plus me-1"></i>
                Register
              </router-link>
            </li>
          </template>
        </ul>
      </div>
    </div>
  </nav>
</template>

<script>
import { mapGetters } from 'vuex'

export default {
  name: 'NavBar',
  data() {
    return {
      isDropdownOpen: false,
      isMobileMenuOpen: false
    }
  },
  computed: {
    ...mapGetters(['user', 'isAuthenticated']),
    homeLink() {
      if (!this.isAuthenticated) {
        return '/'
      }
      if (this.user?.is_admin) {
        return '/admin/dashboard'
      }
      return '/user/dashboard'
    }
  },
  methods: {
    toggleDropdown() {
      this.isDropdownOpen = !this.isDropdownOpen
    },
    closeDropdown() {
      this.isDropdownOpen = false
      this.closeMobileMenu()
    },
    toggleMobileMenu() {
      this.isMobileMenuOpen = !this.isMobileMenuOpen
    },
    closeMobileMenu() {
      this.isMobileMenuOpen = false
    },
    async handleLogout() {
      try {
        await this.$store.dispatch('auth/logout')
        this.closeDropdown()
        this.$router.push('/')
        this.$store.dispatch('setAlert', {
          message: 'Successfully logged out',
          type: 'success'
        })
      } catch (error) {
        console.error('Logout error:', error)
        this.$store.dispatch('setAlert', {
          message: 'Logout failed',
          type: 'error'
        })
      }
    }
  },
  mounted() {
    // Close dropdown when clicking outside
    document.addEventListener('click', (event) => {
      const dropdown = this.$el.querySelector('.dropdown')
      if (dropdown && !dropdown.contains(event.target)) {
        this.isDropdownOpen = false
      }
    })
  }
}
</script>

<style scoped>
/* Component-specific styles if needed */
.navbar {
  transition: all var(--transition-fast);
}

.me-auto {
  margin-right: auto !important;
}

.me-1 {
  margin-right: 0.25rem !important;
}

.me-2 {
  margin-right: 0.5rem !important;
}

.text-md-end {
  text-align: right;
}

@media (max-width: 768px) {
  .text-md-end {
    text-align: left;
  }
}
</style>

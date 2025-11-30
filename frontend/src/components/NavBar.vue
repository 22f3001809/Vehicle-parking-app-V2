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
                <router-link to="/admin/dashboard" class="nav-link" @click="closeMobileMenu">
                  Home
                </router-link>
              </li>
              <li class="nav-item">
                <router-link to="/admin/parking-lots" class="nav-link" @click="closeMobileMenu">
                  <i class="fas fa-parking me-1"></i>
                  Parking Lots
                </router-link>
              </li>
              <li class="nav-item">
                <router-link to="/admin/users" class="nav-link" @click="closeMobileMenu">
                  <i class="fas fa-users me-1"></i>
                  Users
                </router-link>
              </li>
              <li class="nav-item dropdown search-dropdown">
                <a 
                  class="nav-link dropdown-toggle" 
                  href="#" 
                  @click.prevent="toggleSearchDropdown"
                  role="button"
                >
                  <i class="fas fa-search me-1"></i>
                  Search
                </a>
                <div class="dropdown-menu search-menu" :class="{ show: isSearchDropdownOpen }">
                  <div class="search-container p-3">
                    <div class="mb-2">
                      <label class="form-label small">Search By:</label>
                      <select class="form-select form-select-sm" v-model="adminSearchType">
                        <option value="username">Username</option>
                        <option value="parking_lot">Parking Lot Location</option>
                      </select>
                    </div>
                    <div class="input-group input-group-sm">
                      <input
                        type="text"
                        class="form-control"
                        v-model="adminSearchQuery"
                        :placeholder="adminSearchType === 'username' ? 'Search users...' : 'Search by city/pin code...'"
                        @keyup.enter="performAdminSearch"
                      >
                      <button class="btn btn-primary" @click="performAdminSearch">
                        <i class="fas fa-search"></i>
                      </button>
                    </div>
                  </div>
                </div>
              </li>
              <li class="nav-item">
                <router-link to="/admin/summary" class="nav-link" @click="closeMobileMenu">
                  Summary Charts
                </router-link>
              </li>
            </template>
            
            <!-- Regular User Links -->
            <template v-else>
              <li class="nav-item">
                <router-link to="/user/dashboard" class="nav-link" @click="closeMobileMenu">
                  Home
                </router-link>
              </li>
              <li class="nav-item">
                <router-link to="/user/reservations" class="nav-link" @click="closeMobileMenu">
                  My Reservations
                </router-link>
              </li>
              <li class="nav-item">
                <router-link to="/user/summary" class="nav-link" @click="closeMobileMenu">
                  Summary Charts
                </router-link>
              </li>
              
            </template>
          </template>
        </ul>
        
        <!-- Right Side Navigation -->
        <ul class="navbar-nav">
          <!-- User Dropdown when authenticated -->
          <li v-if="isAuthenticated" class="nav-item dropdown user-dropdown">
            <a 
              class="nav-link dropdown-toggle user-menu-toggle" 
              href="#" 
              @click.prevent="toggleDropdown"
              role="button"
            >
              My Account
            </a>
            <ul class="dropdown-menu dropdown-menu-end user-dropdown-menu" :class="{ show: isDropdownOpen }">
              <li>
                <router-link 
                  :to="user?.is_admin ? '/admin/profile' : '/profile'" 
                  class="dropdown-item" 
                  @click="closeDropdown">
                  Profile
                </router-link>
              </li>
              <li>
                <hr class="dropdown-divider">
              </li>
              <li>
                <button @click="handleLogout" class="dropdown-item logout-item">
                  Logout
                </button>
              </li>
            </ul>
          </li>
          
          <!-- Login/Register when not authenticated -->
          <template v-else>
            <li class="nav-item">
              <router-link to="/login" class="nav-link" @click="closeMobileMenu">
                Login
              </router-link>
            </li>
            <li class="nav-item">
              <router-link to="/register" class="nav-link" @click="closeMobileMenu">
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
      isMobileMenuOpen: false,
      isSearchDropdownOpen: false,
      adminSearchType: 'username',
      adminSearchQuery: ''
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
    toggleSearchDropdown() {
      this.isSearchDropdownOpen = !this.isSearchDropdownOpen
    },
    closeSearchDropdown() {
      this.isSearchDropdownOpen = false
    },
    performAdminSearch() {
      if (!this.adminSearchQuery.trim()) {
        this.$store.dispatch('setAlert', {
          message: 'Please enter a search term',
          type: 'warning'
        })
        return
      }
      
      if (this.adminSearchType === 'username') {
        // Navigate to users page with search query
        this.$router.push({
          path: '/admin/users',
          query: { search: this.adminSearchQuery, type: 'username' }
        })
      } else {
        // Navigate to parking lots page with location search
        this.$router.push({
          path: '/admin/parking-lots',
          query: { search: this.adminSearchQuery, type: 'location' }
        })
      }
      
      this.closeSearchDropdown()
      this.closeMobileMenu()
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
      const userDropdown = this.$el.querySelector('.nav-item.dropdown:not(.search-dropdown)')
      if (userDropdown && !userDropdown.contains(event.target)) {
        this.isDropdownOpen = false
      }
      
      const searchDropdown = this.$el.querySelector('.search-dropdown')
      if (searchDropdown && !searchDropdown.contains(event.target)) {
        this.isSearchDropdownOpen = false
      }
    })
  }
}
</script>

<style scoped>
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

.search-dropdown {
  position: relative;
}

.search-menu {
  min-width: 300px;
  padding: 0;
}

.search-container {
  background: white;
  border-radius: 0.375rem;
}

.search-dropdown .dropdown-menu {
  left: 0;
  right: auto;
}

@media (max-width: 991px) {
  .search-menu {
    position: static !important;
    transform: none !important;
    width: 100%;
    border: none;
    box-shadow: none;
  }
}

.user-dropdown {
  position: relative;
}

.user-menu-toggle {
  padding: 0.5rem 0.75rem !important;
  font-size: 0.875rem;
  font-weight: 500;
}

.user-dropdown-menu {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  padding: 0.5rem 0;
  min-width: 160px;
  margin-top: 0.5rem !important;
}

.user-dropdown-menu .dropdown-item {
  padding: 0.625rem 1.25rem;
  font-size: 0.875rem;
  color: #202124;
  transition: all 0.2s ease;
}

.user-dropdown-menu .dropdown-item:hover {
  background-color: #f8f9fa;
  color: #4285f4;
}

.user-dropdown-menu .logout-item {
  color: #dc3545;
}

.user-dropdown-menu .logout-item:hover {
  background-color: #fff5f5;
  color: #c82333;
}

.user-dropdown-menu .dropdown-divider {
  margin: 0.5rem 0;
  border-color: #e0e0e0;
}

@media (max-width: 991px) {
  .user-dropdown-menu {
    position: static !important;
    transform: none !important;
    width: 100%;
    border: none;
    box-shadow: none;
    margin-top: 0 !important;
  }
  
  .user-menu-toggle {
    padding: 0.5rem 1rem !important;
  }
}
</style>

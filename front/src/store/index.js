import { createStore } from 'vuex'
import axios from 'axios'

// Import modules
import auth from './modules/auth'
import parking from './modules/parking'
import admin from './modules/admin'

export default createStore({
  modules: {
    auth,
    parking,
    admin
  },
  
  state: {
    // Global app state
    alert: null,
    loading: false
  },
  mutations: {
    SET_ALERT(state, alert) {
      state.alert = alert
    },
    
    CLEAR_ALERT(state) {
      state.alert = null
    },
    
    SET_LOADING(state, loading) {
      state.loading = loading
    }
  },
  
  actions: {
    setAlert({ commit }, alert) {
      commit('SET_ALERT', alert)
      
      // Auto clear alert after 5 seconds
      if (alert && alert.type !== 'loading') {
        setTimeout(() => {
          commit('CLEAR_ALERT')
        }, 5000)
      }
    },
    
    clearAlert({ commit }) {
      commit('CLEAR_ALERT')
    },
    
    async fetchCurrentUser({ commit }) {
      try {
        const response = await axios.get('/api/auth/me')
        // Backend may return the user object directly or under { user }
        const user = response.data?.user || response.data
        
        commit('auth/SET_USER', user, { root: true })
        
        return user
      } catch (error) {
        commit('auth/LOGOUT', null, { root: true })
        throw error
      }
    },
    
    setLoading({ commit }, loading) {
      commit('SET_LOADING', loading)
    }
  },
  
  getters: {
    alert: state => state.alert || {},
    alertMessage: state => state.alert?.message || '',
    alertType: state => state.alert?.type || 'info',
    loading: state => state.loading || false,
    // Delegate auth-related getters to auth module
    isAuthenticated: (state, getters, rootState) => rootState.auth?.isAuthenticated || false,
    user: (state, getters, rootState) => rootState.auth?.user || null,
    isAdmin: (state, getters, rootState) => rootState.auth?.user?.is_admin || false,
    isUser: (state, getters, rootState) => rootState.auth?.user && !rootState.auth.user.is_admin,
    userName: (state, getters, rootState) => rootState.auth?.user?.full_name || rootState.auth?.user?.username || ''
  }
})
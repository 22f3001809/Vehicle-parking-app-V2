// Auth module for Vuex store
import { api } from '@/services/api'
import axios from 'axios'

export default {
  namespaced: true,
  
  state: {
    token: localStorage.getItem('access_token') || null,
    refreshToken: localStorage.getItem('refresh_token') || null,
    isAuthenticated: false,
    user: null,
    loginLoading: false,
    registerLoading: false
  },
  
  mutations: {
    SET_TOKEN(state, { access_token, refresh_token }) {
      state.token = access_token
      state.refreshToken = refresh_token
      state.isAuthenticated = !!access_token
      
      if (access_token) {
        localStorage.setItem('access_token', access_token)
        localStorage.setItem('refresh_token', refresh_token)
        axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`
      } else {
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        delete axios.defaults.headers.common['Authorization']
      }
    },
    
    SET_USER(state, user) {
      state.user = user
      state.isAuthenticated = !!user
    },
    
    SET_LOGIN_LOADING(state, loading) {
      state.loginLoading = loading
    },
    
    SET_REGISTER_LOADING(state, loading) {
      state.registerLoading = loading
    },
    
    LOGOUT(state) {
      state.token = null
      state.refreshToken = null
      state.user = null
      state.isAuthenticated = false
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      delete axios.defaults.headers.common['Authorization']
    }
  },
  
  actions: {
    async login({ commit, dispatch }, { username, password }) {
      try {
        commit('SET_LOGIN_LOADING', true)
        
        const response = await api.auth.login({
          username,
          password
        })
        
        const { access_token, refresh_token, user } = response.data
        
        commit('SET_TOKEN', { access_token, refresh_token })
        commit('SET_USER', user)
        
        // Set alert in root store
        dispatch('setAlert', {
          message: 'Login successful',
          type: 'success'
        }, { root: true })
        
        return { success: true, user }
      } catch (error) {
        const message = error.response?.data?.error || 'Login failed'
        
        dispatch('setAlert', {
          message,
          type: 'error'
        }, { root: true })
        
        return { success: false, message }
      } finally {
        commit('SET_LOGIN_LOADING', false)
      }
    },
    
    async register({ commit, dispatch }, userData) {
      try {
        commit('SET_REGISTER_LOADING', true)
        
        const response = await api.auth.register(userData)
        
        const { access_token, refresh_token, user } = response.data
        
        commit('SET_TOKEN', { access_token, refresh_token })
        commit('SET_USER', user)
        
        dispatch('setAlert', {
          message: 'Registration successful',
          type: 'success'
        }, { root: true })
        
        return { success: true, user }
      } catch (error) {
        const message = error.response?.data?.error || 'Registration failed'
        
        dispatch('setAlert', {
          message,
          type: 'error'
        }, { root: true })
        
        return { success: false, message }
      } finally {
        commit('SET_REGISTER_LOADING', false)
      }
    },
    
    async fetchCurrentUser({ commit, dispatch }) {
      try {
        const response = await api.auth.getCurrentUser()
        const user = response.data?.user || response.data
        commit('SET_USER', user)
        return user
      } catch (error) {
        // Token might be invalid
        commit('LOGOUT')
        throw error
      }
    },
    
    async refreshAccessToken({ commit, state }) {
      try {
        if (!state.refreshToken) {
          throw new Error('No refresh token available')
        }
        
        const response = await api.auth.refresh()
        
        const { access_token } = response.data
        commit('SET_TOKEN', { 
          access_token, 
          refresh_token: state.refreshToken 
        })
        
        return access_token
      } catch (error) {
        commit('LOGOUT')
        throw error
      }
    },
    
    logout({ commit, dispatch }) {
      commit('LOGOUT')
      dispatch('setAlert', {
        message: 'Logged out successfully',
        type: 'success'
      }, { root: true })
    }
  },
  
  getters: {
    isAuthenticated: state => state.isAuthenticated,
    user: state => state.user,
    isAdmin: state => state.user?.is_admin || false,
    isUser: state => state.user && !state.user.is_admin,
    token: state => state.token,
    loginLoading: state => state.loginLoading,
    registerLoading: state => state.registerLoading
  }
}
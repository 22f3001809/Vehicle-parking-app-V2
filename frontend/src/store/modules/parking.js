// Parking module for Vuex store
import { api } from '@/services/api'

export default {
  namespaced: true,
  
  state: {
    lots: [],
    currentLot: null,
    spots: [],
    userReservations: [],
    userStats: {
      total_reservations: 0,
      active_reservations: 0,
      completed_reservations: 0,
      total_spent: 0
    },
    loading: false,
    spotsLoading: false
  },
  
  mutations: {
    SET_LOTS(state, lots) {
      state.lots = lots
    },
    
    SET_CURRENT_LOT(state, lot) {
      state.currentLot = lot
    },
    
    SET_SPOTS(state, spots) {
      state.spots = spots
    },
    
    SET_USER_RESERVATIONS(state, reservations) {
      state.userReservations = reservations
    },
    
    SET_USER_STATS(state, stats) {
      state.userStats = stats
    },
    
    SET_LOADING(state, loading) {
      state.loading = loading
    },
    
    SET_SPOTS_LOADING(state, loading) {
      state.spotsLoading = loading
    },
    
    ADD_LOT(state, lot) {
      state.lots.push(lot)
    },
    
    UPDATE_LOT(state, updatedLot) {
      const index = state.lots.findIndex(lot => lot.id === updatedLot.id)
      if (index !== -1) {
        state.lots.splice(index, 1, updatedLot)
      }
      
      if (state.currentLot && state.currentLot.id === updatedLot.id) {
        state.currentLot = updatedLot
      }
    },
    
    REMOVE_LOT(state, lotId) {
      state.lots = state.lots.filter(lot => lot.id !== lotId)
      
      if (state.currentLot && state.currentLot.id === lotId) {
        state.currentLot = null
      }
    },
    
    ADD_RESERVATION(state, reservation) {
      state.userReservations.unshift(reservation)
    },
    
    UPDATE_RESERVATION(state, updatedReservation) {
      const index = state.userReservations.findIndex(r => r.id === updatedReservation.id)
      if (index !== -1) {
        state.userReservations.splice(index, 1, updatedReservation)
      }
    }
  },
  
  actions: {
    async fetchLots({ commit, dispatch }) {
      try {
        commit('SET_LOADING', true)
        const response = await api.parking.getPublicLots()
        commit('SET_LOTS', response.data.parking_lots || response.data)
        return response.data.parking_lots || response.data
      } catch (error) {
        dispatch('setAlert', {
          message: 'Failed to load parking lots',
          type: 'error'
        }, { root: true })
        throw error
      } finally {
        commit('SET_LOADING', false)
      }
    },
    
    async fetchLotById({ commit, dispatch }, lotId) {
      try {
        const response = await api.parking.getLotDetails(lotId)
        commit('SET_CURRENT_LOT', response.data)
        return response.data
      } catch (error) {
        dispatch('setAlert', {
          message: 'Failed to load parking lot details',
          type: 'error'
        }, { root: true })
        throw error
      }
    },
    
    async fetchLotSpots({ commit, dispatch }, lotId) {
      try {
        commit('SET_SPOTS_LOADING', true)
        const response = await api.admin.getLotSpots(lotId)
        commit('SET_SPOTS', response.data.spots)
        commit('SET_CURRENT_LOT', response.data.parking_lot)
        return response.data
      } catch (error) {
        dispatch('setAlert', {
          message: 'Failed to load parking spots',
          type: 'error'
        }, { root: true })
        throw error
      } finally {
        commit('SET_SPOTS_LOADING', false)
      }
    },
    
    async createLot({ commit, dispatch }, lotData) {
      try {
        const response = await api.admin.createParkingLot(lotData)
        commit('ADD_LOT', response.data.lot)
        
        dispatch('setAlert', {
          message: 'Parking lot created successfully',
          type: 'success'
        }, { root: true })
        
        return response.data.lot
      } catch (error) {
        const message = error.response?.data?.error || 'Failed to create parking lot'
        dispatch('setAlert', {
          message,
          type: 'error'
        }, { root: true })
        throw error
      }
    },
    
    async updateLot({ commit, dispatch }, { lotId, lotData }) {
      try {
        const response = await api.admin.updateParkingLot(lotId, lotData)
        commit('UPDATE_LOT', response.data.lot)
        
        dispatch('setAlert', {
          message: 'Parking lot updated successfully',
          type: 'success'
        }, { root: true })
        
        return response.data.lot
      } catch (error) {
        const message = error.response?.data?.error || 'Failed to update parking lot'
        dispatch('setAlert', {
          message,
          type: 'error'
        }, { root: true })
        throw error
      }
    },
    
    async deleteLot({ commit, dispatch }, lotId) {
      try {
        await api.admin.deleteParkingLot(lotId)
        commit('REMOVE_LOT', lotId)
        
        dispatch('setAlert', {
          message: 'Parking lot deleted successfully',
          type: 'success'
        }, { root: true })
        
        return true
      } catch (error) {
        const message = error.response?.data?.error || 'Failed to delete parking lot'
        dispatch('setAlert', {
          message,
          type: 'error'
        }, { root: true })
        throw error
      }
    },
    
    async fetchUserReservations({ commit, dispatch }) {
      try {
        const response = await api.user.getReservations()
        commit('SET_USER_RESERVATIONS', response.data.reservations || [])
        return response.data.reservations
      } catch (error) {
        dispatch('setAlert', {
          message: 'Failed to load reservations',
          type: 'error'
        }, { root: true })
        throw error
      }
    },
    
    async fetchUserStats({ commit, dispatch }) {
      try {
        const response = await api.user.getDashboard()
        commit('SET_USER_STATS', response.data.stats || response.data)
        return response.data.stats || response.data
      } catch (error) {
        dispatch('setAlert', {
          message: 'Failed to load user statistics',
          type: 'error'
        }, { root: true })
        throw error
      }
    },
    
    async bookSpot({ commit, dispatch }, bookingData) {
      try {
        const response = await api.user.bookSpot(bookingData)
        commit('ADD_RESERVATION', response.data.reservation)
        
        dispatch('setAlert', {
          message: 'Parking spot booked successfully',
          type: 'success'
        }, { root: true })
        
        return response.data.reservation
      } catch (error) {
        const message = error.response?.data?.error || 'Failed to book parking spot'
        dispatch('setAlert', {
          message,
          type: 'error'
        }, { root: true })
        throw error
      }
    },
    
    async cancelReservation({ commit, dispatch }, reservationId) {
      try {
        const response = await api.user.cancelReservation(reservationId)
        commit('UPDATE_RESERVATION', response.data.reservation)
        
        dispatch('setAlert', {
          message: 'Reservation cancelled successfully',
          type: 'success'
        }, { root: true })
        
        return response.data.reservation
      } catch (error) {
        const message = error.response?.data?.error || 'Failed to cancel reservation'
        dispatch('setAlert', {
          message,
          type: 'error'
        }, { root: true })
        throw error
      }
    }
  },
  
  getters: {
    allLots: state => state.lots,
    availableLots: state => state.lots.filter(lot => lot.is_active),
    currentLot: state => state.currentLot,
    lotSpots: state => state.spots,
    availableSpots: state => state.spots.filter(spot => spot.status === 'A'),
    occupiedSpots: state => state.spots.filter(spot => spot.status === 'O'),
    userReservations: state => state.userReservations,
    activeReservations: state => state.userReservations.filter(r => r.status === 'active'),
    userStats: state => state.userStats,
    loading: state => state.loading,
    spotsLoading: state => state.spotsLoading
  }
}
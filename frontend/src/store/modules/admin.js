import api from '@/services/api';

const state = {
    lots: [],
    users: [],
    reservations: [],
    stats: {},
    loading: false,
};

const getters = {
    allLots: state => state.lots,
    allUsers: state => state.users,
    allReservations: state => state.reservations,
    dashboardStats: state => state.stats,
    isLoading: state => state.loading,
};

const actions = {
    async fetchDashboardStats({ commit }) {
        commit('setLoading', true);
        try {
            const response = await api.get('/admin/dashboard');
            commit('setStats', response.data);
        } catch (error) {
            console.error('Error fetching admin dashboard stats:', error);
            // Optionally, commit an error state
        } finally {
            commit('setLoading', false);
        }
    },
    async fetchLots({ commit }) {
        commit('setLoading', true);
        try {
            const response = await api.get('/admin/parking-lots');
            commit('setLots', response.data);
        } catch (error) {
            console.error('Error fetching parking lots:', error);
        } finally {
            commit('setLoading', false);
        }
    },
    async addLot({ commit }, lotData) {
        try {
            const response = await api.post('/admin/parking-lots', lotData);
            commit('addLot', response.data.lot);
            return response;
        } catch (error) {
            console.error('Error adding parking lot:', error);
            throw error;
        }
    },
    async updateLot({ commit }, { id, data }) {
        try {
            const response = await api.put(`/admin/parking-lots/${id}`, data);
            commit('updateLot', response.data.lot);
            return response;
        } catch (error) {
            console.error('Error updating parking lot:', error);
            throw error;
        }
    },
    async deleteLot({ commit }, id) {
        try {
            await api.delete(`/admin/parking-lots/${id}`);
            commit('deleteLot', id);
        } catch (error) {
            console.error('Error deleting parking lot:', error);
            throw error;
        }
    },
};

const mutations = {
    setLoading: (state, loading) => (state.loading = loading),
    setStats: (state, stats) => (state.stats = stats),
    setLots: (state, lots) => (state.lots = lots),
    addLot: (state, lot) => state.lots.unshift(lot),
    updateLot: (state, updatedLot) => {
        const index = state.lots.findIndex(lot => lot.id === updatedLot.id);
        if (index !== -1) {
            state.lots.splice(index, 1, updatedLot);
        }
    },
    deleteLot: (state, id) => {
        state.lots = state.lots.filter(lot => lot.id !== id);
    },
};

export default {
    namespaced: true,
    state,
    getters,
    actions,
    mutations,
};

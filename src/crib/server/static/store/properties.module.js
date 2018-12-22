import { propertiesService } from '../services/index.js';

export const properties = {
  namespaced: true,
  state: {
    gettingLocations: false,
    locations: []
  },
  actions: {
    getLocations({ commit }) {
      commit('locationsRequest');

      propertiesService.locations()
        .then(
          locations => {
            commit('setLocations', locations);
          },
          error => {
            commit('locationsError', error);
            dispatch('alert/error', error, {root: true});
          }
        );
    }
  },
  mutations: {
    locationsRequest(state) {
      state.gettingLocations = true;
    },
    setLocations(state, locations) {
      state.gettingLocations = false;
      state.locations = locations;
    },
    locationsError(state) {
      state.gettingLocations = false;
    }
  }
}

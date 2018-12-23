import { propertiesService } from '../services/index.js';

export const properties = {
  namespaced: true,
  state: {
    gettingProperties: false,
    properties: []
  },
  actions: {
    getProperties({ commit }) {
      commit('propertyRequest');

      propertiesService.find()
        .then(
          properties => {
            commit('setProperties', properties);
          },
          error => {
            commit('propertiesError', error);
            dispatch('alert/error', error.message, {root: true});
          }
        );
    }
  },
  mutations: {
    propertyRequest(state) {
      state.gettingProperties = true;
    },
    setProperties(state, properties) {
      state.gettingProperties = false;
      state.properties = properties;
    },
    propertiesError(state) {
      state.gettingProperties = false;
    }
  }
}

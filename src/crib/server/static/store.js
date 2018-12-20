// imports of AJAX functions will go here
const state = {
  // single source of data
  username: '',
  jwt: ''
};

const actions = {
  // asynchronous operations
  login (context, userData) {
      context.commit('setUserData', { userData });
      return authenticate(userData)
          .then(response => context.commit('setJwtToken', { jwt: response.data }))
          .catch(function(error) {
              console.log('Error Authenticating: ', error);
              EventBus.$emit('failedAuthentication', error);
          });
  },
  register (context, userData) {
      context.commit('setUserData', { userData });
      return register(userData)
          .then(response => context.dispatch('login', userData))
          .catch(function(error) {
              console.log('Error Registering: ', error);
              EventBus.$emit('failedRegistering', error);
          });
  }
};

const mutations = {
  // isolated data mutations
  setUserData (state, payload) {
      state.username = payload.userData.username;
  },
  setJwtToken (state, payload) {
      localStorage.access_token = payload.jwt.access_token;
      localStorage.refresh_token = payload.jwt.refresh_token;
      state.jwt = payload.jwt;
  }
};

const getters = {
    // reusable data accessors
    isAuthenticated (state) {
        return isValidJwt(state.jwt.access_token);
    },
    username (state) {
        return state.username;
    }
};

const store = new Vuex.Store({
  state,
  actions,
  mutations,
  getters
});

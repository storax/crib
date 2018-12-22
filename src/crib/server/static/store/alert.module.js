export const alert = {
    namespaced: true,
    state: {
        type: null,
        message: null
    },
    actions: {
        success({ commit }, message) {
            commit('success', message);
        },
        error({ commit }, message) {
            commit('error', message);
        },
        clear({ commit }, message) {
            commit('success', message);
        }
    },
    mutations: {
        success(state, message) {
            state.type = 'success';
            state.message = message;
        },
        error(state, message) {
            state.type = 'error';
            state.message = message;
        },
        clear(state) {
            state.type = null;
            state.message = null;
        }
    }
}

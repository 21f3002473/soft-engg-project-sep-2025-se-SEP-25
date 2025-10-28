import { createStore } from 'vuex';

const store = createStore({
    state: {
        BASEURL: 'http://localhost:3000',
        TOKEN: null,
        USER: null,
        role: null,
    },
    mutations: {
        setToken(state, token) {
            state.TOKEN = token;
        },
        setUser(state, user) {
            state.USER = user;
        },
        setRole(state, role) {
            state.role = role;
        },
        clearAll(state) {
            state.TOKEN = null;
            state.USER = null;
            state.role = null;
        },
    },
    actions: {
        updateToken({ commit }, token) {
            commit('setToken', token);
        },
        updateUser({ commit }, user) {
            commit('setUser', user);
        },
        clearAll({ commit }) {
            commit('clearAll');
        },
    },
});

export default store;

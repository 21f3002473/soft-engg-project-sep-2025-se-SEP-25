import { createStore } from 'vuex';

const store = createStore({
    state: {
        BASEURL: 'http://localhost:8000',
        TOKEN: null,
        USER: null,
        role: null,
        is_authenticated: false,
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
        setAuthentication(state, status) {
            state.is_authenticated = status;
        },
    },
    actions: {
        updateToken({ commit }, token) {
            commit('setToken', token);
        },
        updateUser({ commit }, user) {
            commit('setUser', user);
        },
        updateRole({ commit }, role) {
            commit('setRole', role);
        },
        updateAuthentication({ commit }, status) {
            commit('setAuthentication', status);
        },
        clearAll({ commit }) {
            commit('clearAll');
        },
    },
});

export default store;

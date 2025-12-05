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
            state.is_authenticated = false;
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
        initializeStore({ commit }) {
            const token = localStorage.getItem('token');
            const user = localStorage.getItem('user');

            if (token) {
                commit('setToken', token);
                commit('setAuthentication', true);
            }

            if (user) {
                try {
                    const parsedUser = JSON.parse(user);
                    commit('setUser', parsedUser);

                    let role = parsedUser.role;
                    if (role === "root") role = "admin";
                    else if (role === "pm") role = "productmanager";

                    commit('setRole', role);
                } catch (e) {
                    console.error('Error parsing user data:', e);
                }
            }
        },
        logout({ commit }) {
            commit('clearAll');
            localStorage.removeItem('token');
            localStorage.removeItem('user');
        },
    },
});

export default store;
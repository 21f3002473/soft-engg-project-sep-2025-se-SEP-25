import { createApp } from 'vue'
import App from './App.vue'
import router from './router/router.js'
import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap-icons/font/bootstrap-icons.css'
import 'katex/dist/katex.min.css'
import store from './store/store.js'
import Vue3Toastify from 'vue3-toastify';
import 'vue3-toastify/dist/index.css';

const app = createApp(App)
app.use(store)
app.use(router)
app.use(Vue3Toastify, {
    autoClose: 3000,
    position: "top-center",
});

store.dispatch('initializeStore')
app.mount('#app')
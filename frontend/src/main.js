import { createApp } from 'vue'
import App from './App.vue'
import router from './router/router.js'
import store from './store/store.js'
import Vue3Toastify from 'vue3-toastify'
import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap-icons/font/bootstrap-icons.css'
import 'katex/dist/katex.min.css'
import 'vue3-toastify/dist/index.css'

const app = createApp(App)
app.use(store)
app.use(router)
app.use(Vue3Toastify, {
    autoClose: 3000,
    position: "top-center",
    clearOnUrlChange: false,
    theme: "colored",
    transition: "slide",
    hideProgressBar: false,
    newestOnTop: true,
});

store.dispatch('initializeStore')
app.mount('#app')
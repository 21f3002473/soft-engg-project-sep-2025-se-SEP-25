import { createApp } from 'vue'
import App from './App.vue'
import router from './router/router.js'
import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap-icons/font/bootstrap-icons.css'
import 'katex/dist/katex.min.css'
import store from './store/store.js'

const app = createApp(App)
app.use(store)
app.use(router)
store.dispatch('initializeStore')
app.mount('#app')
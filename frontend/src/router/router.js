import {createRouter , createWebHistory} from 'vue-router';

import AdminDashboard from "@/components/admins/Dashboard.vue";
import LoginPageView from '@/components/Landing/LoginPageView.vue';

const routes = [
    {
        path: '/',
        name: 'AdminDashboard',
        component: AdminDashboard
    },
    {
        path: '/login',
        name: 'LoginPage',
        component: LoginPageView
    }
]

const router = createRouter({
    history: createWebHistory(process.env.BASE_URL),
    routes
})

// write the middleware later next pull request

export default router;
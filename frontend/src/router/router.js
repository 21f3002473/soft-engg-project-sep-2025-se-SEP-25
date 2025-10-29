import {createRouter , createWebHistory} from 'vue-router';

import AdminDashboard from "@/components/admins/Dashboard.vue";
import LoginPageView from '@/components/Landing/LoginPageView.vue';
import LandingView from '@/components/Landing/LandingView.vue';

const routes = [
    {
        path: '/',
        name: 'LandingView',
        component: LandingView
    },
    {
        path: '/adminDashboard',
        name: 'AdminDashboard',
        component: AdminDashboard
    },
    {
        path: '/login',
        name: 'LoginPage',
        component: LoginPageView
    },
    {
        path: '/adminRegister',
        name: 'AdminRegister',
        component: () => import('@/components/admins/RegistrationViewPage.vue')
    },
]

const router = createRouter({
    history: createWebHistory(process.env.BASE_URL),
    routes
})

// write the middleware later next pull request

export default router;
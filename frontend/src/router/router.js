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
        path: '/admin/dashboard',
        name: 'AdminDashboard',
        component: () => import('@/components/admins/Dashboard.vue'),
    },
    {
        path: '/user/dashboard',
        name: 'UserDashboard',
        component: () => import('@/components/users/Dashboard.vue'),
    },
    {
        path: '/productmanager/dashboard',
        name: 'ProductmanagerDashboard',
        component: () => import('@/components/productmanager/Dashboard.vue'),
    },
    {
        path: '/hr/dashboard',
        name: 'HRDashboard',
        component: () => import('@/components/hr/Dashboard.vue'),
    },
    {
        path: '/hr/chatbot',
        name: 'HRChatbot',
        component: () => import('@/components/hr/Chatbot.vue')
    },

]

const router = createRouter({
    history: createWebHistory(process.env.BASE_URL),
    routes
})

// write the middleware later next pull request

export default router;
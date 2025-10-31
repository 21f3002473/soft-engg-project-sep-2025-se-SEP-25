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
        path: '/hr',
        component: () => import('@/components/hr/HRLayout.vue'),
        children: [
        {
            path: '', // default child route (opens first)
            name: 'HRDashboard',
            component: () => import('@/components/hr/Dashboard.vue'),
        },
        {
            path: 'chatbot',
            name: 'HRChatbot',
            component: () => import('@/components/hr/Chatbot.vue'),
        },
        {
            path: 'employees',
            name: 'HREmployees',
            component: () => import('@/components/hr/Employees.vue'),
        },
        {
            path: 'hrpolicies',
            name: 'HRPolicies',
            component: () => import('@/components/hr/HrPolicies.vue'),
        },
        {
            path: 'projects',
            name: 'HRProjects',
            component: () => import('@/components/hr/Projects.vue'),
        },
    ],
    },

]

const router = createRouter({
    history: createWebHistory(process.env.BASE_URL),
    routes
})

// write the middleware later next pull request

export default router;
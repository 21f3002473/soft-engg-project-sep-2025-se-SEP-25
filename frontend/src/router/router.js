import { createRouter, createWebHistory } from 'vue-router';

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
        path: '/user',
        component: () => import('@/components/users/UserLayout.vue'),
        children: [
            {
                path: 'dashboard',
                name: 'UserDashboard',
                component: () => import('@/components/users/UserDashboard.vue'),
            },
            {
                path: 'requests',
                name: 'UserRequests',
                component: () => import('@/components/users/UserRequests.vue'),
            },
            {
                path: 'hr-faqs',
                name: 'UserHRFAQs',
                component: () => import('@/components/users/UserHRFAQs.vue'),
            },
            {
                path: 'learning',
                name: 'UserLearning',
                component: () => import('@/components/users/UserLearning.vue'),
            },
            {
                path: 'writing-section',
                name: 'UserWritingSection',
                component: () => import('@/components/users/UserWritingSection.vue'),
            },
            {
                path: 'account',
                name: 'UserAccount',
                component: () => import('@/components/users/UserAccount.vue'),
            }
        ],
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
        path: '/backups',
        name: 'Backups',
        component: () => import('@/components/admins/dataBackup.vue'),
    },
]

const router = createRouter({
    history: createWebHistory(process.env.BASE_URL),
    routes
})

export default router;
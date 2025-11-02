import { createRouter, createWebHistory } from 'vue-router';

// import AdminDashboard from "@/components/admins/Dashboard.vue";
// import LoginPageView from '@/components/landing/LoginPageView.vue';
// import LandingView from '@/components/landing/LandingView.vue';

const routes = [
    {
        path: '/',
        name: 'LandingView',
        component: () => import('@/components/Landing/LandingView.vue'),
    },
    {
        path: '/login',
        name: 'LoginPage',
        // component: LoginPageView
        component: () => import('@/components/Landing/LoginPageView.vue'),
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
        path: '/productmanager',
        component: () => import('@/components/productmanager/fragments/navbarcomponent.vue'),
        meta: { requiresAuth: true },
        children: [
            {
                path: 'dashboard',
                name: 'ProductManagerDashboard',
                component: () => import('@/components/productmanager/Dashboard.vue'),
            },
            {
                // this is the nested route under dashboard to show client requirements
                path: 'dashboard/requirements/:clientId',
                name: 'ProductManagerRequirements',
                component: () => import('@/components/productmanager/ClientRequirementsView.vue'),
                props: (route) => ({ clientId: route.params.clientId })
            },
            {
                path: 'clientsUpdate',
                name: 'ProductManagerClientsUpdate',
                component: () => import('@/components/productmanager/ClientUpdateView.vue'),
            },
            {
                path: 'clientsUpdate/:id',
                name: 'ProductManagerClientsUpdateDetails',
                component: () => import('@/components/productmanager/UpdateClientView.vue'),
                props: (route) => ({ clientID: route.params.id })
            },
            {
                path: 'projects',
                name: 'ProductManagerProjects',
                component: () => import('@/components/productmanager/ProjectsView.vue'),
            }, // will dev this in milestone 
            {
                path: 'performance',
                name: 'ProductManagerPerformance',
                component: () => import('@/components/productmanager/PerformanceView.vue'),
            },
            {
                path: 'performance/:id',
                name: 'ProductManagerPerformanceDetails',
                component: () => import('@/components/productmanager/EmployeePerformanceView.vue'),
                props: (route) => ({ employeeId: route.params.id })
            }
        ],
    },
    
    {
        path: '/hr',
        component: () => import('@/components/hr/HRLayout.vue'),
        children: [
        {
            path: '', // default child route (opens first)
            index: true,
            name: 'dashboard',
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
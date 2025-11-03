import { createRouter, createWebHistory } from 'vue-router';

const routes = [
    {
        path: '/',
        name: 'Landing',
        component: () => import('@/components/landing/LandingView.vue'),
    },
    {
        path: '/login',
        name: 'Login',
        component: () => import('@/components/landing/LoginPageView.vue'),
    },
    {
        path: '/admin',
        component: () => import('@/components/admin/Layout.vue'),
        children: [
            {
            path: 'dashboard', 
            name: 'AdminDashboard',
            component: () => import('@/components/admin/Dashboard.vue'),
            },
            {
            path: 'backups',
            name: 'AdminBackups',
            component: () => import('@/components/admin/DataBackup.vue'),
            },
            {
                path: 'SystemStatus',                
                name: 'AdminSystemStatus',
                component: () => import('@/components/admin/SystemStatus.vue'),
            },
            {
                path: 'logs',
                name: 'AdminLogs',
                component: () => import('@/components/admin/Logs.vue'),
            },
            {
                path: 'updates',
                name: 'AdminUpdates',
                component: () => import('@/components/admin/Updates.vue'),
            },
            {
                path: 'accounts',
                name: 'AdminAccount',
                component: () => import('@/components/admin/Accounts.vue'),
            },
        ],
    },
    {
        path: '/employee',
        component: () => import('@/components/employee/Layout.vue'),
        children: [
            {
                path: 'dashboard',
                name: 'EmployeeDashboard',
                component: () => import('@/components/employee/Dashboard.vue'),
            },
            {
                path: 'requests',
                name: 'EmployeeRequests',
                component: () => import('@/components/employee/Requests.vue'),
                children: [
                    {
                        path: 'leave',
                        name: 'EmployeeLeaveForm',
                        component: () => import('@/components/employee/fragments/LeaveForm.vue'),
                    },
                    {
                        path: 'reimbursement',
                        name: 'EmployeeReimbursementForm',
                        component: () => import('@/components/employee/fragments/ReimbursementForm.vue'),
                    },
                    {
                        path: 'transfer',
                        name: 'EmployeeTransferForm',
                        component: () => import('@/components/employee/fragments/TransferForm.vue'),
                    }
                ]
            },
            {
                path: 'hr-faqs',
                name: 'EmployeeHRFAQs',
                component: () => import('@/components/employee/HRFAQs.vue'),
            },
            {
                path: 'learning',
                name: 'EmployeeLearning',
                component: () => import('@/components/employee/Learning.vue'),
            },
            {
                path: 'writing',
                name: 'EmployeeWriting',
                component: () => import('@/components/employee/Writing.vue'),
            },
            {
                path: 'account',
                name: 'EmployeeAccount',
                component: () => import('@/components/employee/Account.vue'),
            }
        ],
    },
    {
        path: '/productmanager',
        component: () => import('@/components/productmanager/fragments/NavBar.vue'),
        meta: { requiresAuth: true },
        children: [
            {
                path: 'dashboard',
                name: 'ProductManagerDashboard',
                component: () => import('@/components/productmanager/Dashboard.vue'),
            },
            {
                path: 'dashboard/requirements/:clientId',
                name: 'ProductManagerRequirements',
                component: () => import('@/components/productmanager/ClientRequirements.vue'),
                props: (route) => ({ clientId: route.params.clientId })
            },
            {
                path: 'clientsUpdate',
                name: 'ProductManagerClientsUpdate',
                component: () => import('@/components/productmanager/ClientUpdate.vue'),
            },
            {
                path: 'clientsUpdate/:id',
                name: 'ProductManagerClientsUpdateDetails',
                component: () => import('@/components/productmanager/UpdateClient.vue'),
                props: (route) => ({ clientID: route.params.id })
            },
            {
                path: 'projects',
                name: 'ProductManagerProjects',
                component: () => import('@/components/productmanager/Projects.vue'),
            },
            {
                path: 'performance',
                name: 'ProductManagerPerformance',
                component: () => import('@/components/productmanager/Performance.vue'),
            },
            {
                path: 'performance/:id',
                name: 'ProductManagerPerformanceDetails',
                component: () => import('@/components/productmanager/EmployeePerformance.vue'),
                props: (route) => ({ employeeId: route.params.id })
            }
        ],
    },
    
    {
        path: '/hr',
        component: () => import('@/components/hr/Layout.vue'),
        children: [
        {
            path: 'dashboard',
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
            component: () => import('@/components/hr/HRPolicies.vue'),
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

export default router;
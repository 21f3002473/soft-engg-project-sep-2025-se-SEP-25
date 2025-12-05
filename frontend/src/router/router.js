import { createRouter, createWebHistory } from 'vue-router';
import store from '@/store/store.js';

const routes = [
    {
        path: '/',
        name: 'Landing',
        component: () => import('@/components/Landing/LandingView.vue'),
    },
    {
        path: '/login',
        name: 'Login',
        component: () => import('@/components/Landing/LoginPage.vue'),
    },
    {
        path: '/logout',
        name: 'Logout',
        component: () => import('@/components/Landing/LoginPage.vue'),
    },
    {
        path: '/adminregister',
        name: 'AdminRegistration',
        component: () => import('@/components/admin/AdminRegistration.vue'),
    },
    {
        path: '/admin',
        component: () => import('@/components/admin/AdminLayout.vue'),
        meta: { requiresAuth: true, role: 'admin' },
        children: [
            {
                path: '',
                redirect: 'admin/dashboard',
            },
            {
                path: 'dashboard',
                name: 'AdminDashboard',
                component: () => import('@/components/admin/AdminDashboard.vue'),
            },
            {
                path: 'backups',
                name: 'AdminBackups',
                component: () => import('@/components/admin/AdminDataBackup.vue'),
            },
            {
                path: 'add-employee',
                name: 'AdminAddEmployee',
                component: () => import('@/components/admin/AdminAddEmployee.vue'),
            },
            {
                path: 'logs',
                name: 'AdminLogs',
                component: () => import('@/components/admin/AdminLogs.vue'),
            },
            {
                path: 'updates',
                name: 'AdminUpdates',
                component: () => import('@/components/admin/AdminUpdates.vue'),
            },
            {
                path: 'account',
                name: 'AdminAccount',
                component: () => import('@/components/admin/AdminAccount.vue'),
            },
        ],
    },
    {
        path: '/employee',
        component: () => import('@/components/employee/EmployeeLayout.vue'),
        meta: { requiresAuth: true, role: 'employee' },
        children: [
            {
                path: '',
                redirect: 'employee/dashboard',
            },
            {
                path: 'dashboard',
                name: 'EmployeeDashboard',
                component: () => import('@/components/employee/EmployeeDashboard.vue'),
            },
            {
                path: 'requests',
                name: 'EmployeeRequests',
                component: () => import('@/components/employee/EmployeeRequests.vue'),
                children: [
                    {
                        path: 'leave',
                        name: 'EmployeeLeaveForm',
                        component: () => import('@/components/employee/fragments/EmployeeLeaveForm.vue'),
                    },
                    {
                        path: 'leave/:leave_id',
                        name: 'EmployeeLeaveDetail',
                        component: () => import('@/components/employee/fragments/EmployeeLeaveDetail.vue'),
                        props: (route) => ({ leaveID: route.params.leave_id })
                    },
                    {
                        path: 'reimbursement',
                        name: 'EmployeeReimbursementForm',
                        component: () => import('@/components/employee/fragments/EmployeeReimbursementForm.vue'),
                    },
                    {
                        path: 'reimbursement/:reimbursement_id',
                        name: 'EmployeeReimbursementDetail',
                        component: () => import('@/components/employee/fragments/EmployeeReimbursementDetail.vue'),
                        props: (route) => ({ reimbursementID: route.params.reimbursement_id })
                    },
                    {
                        path: 'transfer',
                        name: 'EmployeeTransferForm',
                        component: () => import('@/components/employee/fragments/EmployeeTransferForm.vue'),
                    },
                    {
                        path: 'transfer/:transfer_id',
                        name: 'EmployeeTransferDetail',
                        component: () => import('@/components/employee/fragments/EmployeeTransferDetail.vue'),
                        props: (route) => ({ transferID: route.params.transfer_id })
                    }
                ]
            },
            {
                path: 'hr-faqs',
                name: 'EmployeeHRFAQs',
                component: () => import('@/components/employee/EmployeeHRFAQs.vue'),
            },
            {
                path: 'learning',
                name: 'EmployeeLearning',
                component: () => import('@/components/employee/EmployeeLearning.vue'),
            },
            {
                path: 'writing',
                name: 'EmployeeWriting',
                component: () => import('@/components/employee/EmployeeWriting.vue'),
            },
            {
                path: 'account',
                name: 'EmployeeAccount',
                component: () => import('@/components/employee/EmployeeAccount.vue'),
            }
        ],
    },
    {
        path: '/productmanager',
        component: () => import('@/components/productmanager/fragments/ProductManagerNavBar.vue'),
        meta: { requiresAuth: true, role: 'productmanager' },
        children: [
            {
                path: '',
                redirect: 'productmanager/dashboard',
            },
            {
                path: 'dashboard',
                name: 'ProductManagerDashboard',
                component: () => import('@/components/productmanager/ProductMangerDashboard.vue'),
            },
            {
                path: 'dashboard/requirements/:clientId',
                name: 'ProductManagerRequirements',
                component: () => import('@/components/productmanager/ProductMangerClientRequirements.vue'),
                props: (route) => ({ clientId: route.params.clientId })
            },
            {
                path: 'clients-update',
                name: 'ProductManagerClientsUpdate',
                component: () => import('@/components/productmanager/ProductMangerClientUpdate.vue'),
            },
            {
                path: 'clients-update/:id',
                name: 'ProductManagerClientsUpdateDetails',
                component: () => import('@/components/productmanager/ProductMangerUpdateClient.vue'),
                props: (route) => ({ clientID: route.params.id })
            },
            {
                path: 'projects',
                name: 'ProductManagerProjects',
                component: () => import('@/components/productmanager/ProductMangerProjects.vue'),
            },
            {
                path: 'performance',
                name: 'ProductManagerPerformance',
                component: () => import('@/components/productmanager/ProductMangerPerformance.vue'),
            },
            {
                path: 'performance/:id',
                name: 'ProductManagerPerformanceDetails',
                component: () => import('@/components/productmanager/ProductMangerEmployeePerformance.vue'),
                props: (route) => ({ employeeId: route.params.id })
            }
        ],
    },

    {
        path: '/hr',
        component: () => import('@/components/hr/HRLayout.vue'),
        meta: { requiresAuth: true, role: 'hr' },
        children: [
            {
                path: '',
                redirect: 'hr/dashboard',
            },
            {
                path: 'dashboard',
                name: 'HRDashboard',
                component: () => import('@/components/hr/HRDashboard.vue'),
            },
            {
                path: 'chatbot',
                name: 'HRChatbot',
                component: () => import('@/components/hr/HRChatbot.vue'),
            },
            {
                path: 'employees',
                name: 'HREmployees',
                component: () => import('@/components/hr/HREmployees.vue'),
            },
            {
                path: 'hrpolicies',
                name: 'HRPolicies',
                component: () => import('@/components/hr/HRPolicies.vue'),
            },
            {
                path: 'projects',
                name: 'HRProjects',
                component: () => import('@/components/hr/HRProjects.vue'),
            },
        ],
    },
]

const router = createRouter({
    history: createWebHistory(process.env.BASE_URL),
    routes
})

router.beforeEach((to, from, next) => {
    const requiresAuth = to.matched.some(record => record.meta.requiresAuth);
    const token = store.state.TOKEN || localStorage.getItem('token');

    let userRole = store.state.role;
    if (!userRole && token) {
        const user = localStorage.getItem('user');
        if (user) {
            try {
                const parsed = JSON.parse(user);
                let r = parsed.role;
                if (r === "root") r = "admin";
                else if (r === "pm") r = "productmanager";
                userRole = r;
            } catch (e) { 
                console.log(e);
                userRole = null;
            }
        }
    }

    if (requiresAuth) {
        if (!token) {
            next('/login');
        } else {
            const requiredRole = to.matched.find(record => record.meta.role)?.meta.role;

            if (requiredRole && requiredRole !== userRole) {
                if (userRole === 'admin') next('/admin/dashboard');
                else if (userRole === 'employee') next('/employee/dashboard');
                else if (userRole === 'hr') next('/hr/dashboard');
                else if (userRole === 'productmanager') next('/productmanager/dashboard');
                else next('/login');
            } else {
                next();
            }
        }
    } else {
        if (token && (to.path === '/login' || to.path === '/')) {
            if (userRole === 'admin') next('/admin/dashboard');
            else if (userRole === 'employee') next('/employee/dashboard');
            else if (userRole === 'hr') next('/hr/dashboard');
            else if (userRole === 'productmanager') next('/productmanager/dashboard');
            else next();
        } else {
            next();
        }
    }
});

export default router;
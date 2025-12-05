import { createRouter, createWebHistory } from 'vue-router';

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
        children: [
            { path: '', name: 'AdminDashboard', component: () => import('@/components/admin/AdminDashboard.vue') },
            { path: 'backups', name: 'AdminBackups', component: () => import('@/components/admin/AdminDataBackup.vue') },
            { path: 'add-employee', name: 'AdminAddEmployee', component: () => import('@/components/admin/AdminAddEmployee.vue') },
            { path: 'logs', name: 'AdminLogs', component: () => import('@/components/admin/AdminLogs.vue') },
            { path: 'updates', name: 'AdminUpdates', component: () => import('@/components/admin/AdminUpdates.vue') },
            { path: 'account', name: 'AdminAccount', component: () => import('@/components/admin/AdminAccount.vue') },
        ],
    },
    {
        path: '/employee',
        component: () => import('@/components/employee/EmployeeLayout.vue'),
        children: [
            { path: 'dashboard', name: 'EmployeeDashboard', component: () => import('@/components/employee/EmployeeDashboard.vue') },
            {
                path: 'requests',
                name: 'EmployeeRequests',
                component: () => import('@/components/employee/EmployeeRequests.vue'),
                children: [
                    { path: 'leave', name: 'EmployeeLeaveForm', component: () => import('@/components/employee/fragments/EmployeeLeaveForm.vue') },
                    { path: 'leave/:leave_id', name: 'EmployeeLeaveDetail', component: () => import('@/components/employee/fragments/EmployeeLeaveDetail.vue'), props: r => ({ leaveID: r.params.leave_id }) },
                    { path: 'reimbursement', name: 'EmployeeReimbursementForm', component: () => import('@/components/employee/fragments/EmployeeReimbursementForm.vue') },
                    { path: 'reimbursement/:reimbursement_id', name: 'EmployeeReimbursementDetail', component: () => import('@/components/employee/fragments/EmployeeReimbursementDetail.vue'), props: r => ({ reimbursementID: r.params.reimbursement_id }) },
                    { path: 'transfer', name: 'EmployeeTransferForm', component: () => import('@/components/employee/fragments/EmployeeTransferForm.vue') },
                    { path: 'transfer/:transfer_id', name: 'EmployeeTransferDetail', component: () => import('@/components/employee/fragments/EmployeeTransferDetail.vue'), props: r => ({ transferID: r.params.transfer_id }) },
                ]
            },
            { path: 'hr-faqs', name: 'EmployeeHRFAQs', component: () => import('@/components/employee/EmployeeHRFAQs.vue') },
            { path: 'learning', name: 'EmployeeLearning', component: () => import('@/components/employee/EmployeeLearning.vue') },
            { path: 'writing', name: 'EmployeeWriting', component: () => import('@/components/employee/EmployeeWriting.vue') },
            { path: 'account', name: 'EmployeeAccount', component: () => import('@/components/employee/EmployeeAccount.vue') },
        ],
    },
    {
        path: '/productmanager',
        component: () => import('@/components/productmanager/fragments/ProductManagerNavBar.vue'),
        meta: { requiresAuth: true },
        children: [
            { path: 'dashboard', name: 'ProductManagerDashboard', component: () => import('@/components/productmanager/ProductMangerDashboard.vue') },
            { path: 'dashboard/requirements/:clientId', name: 'ProductManagerRequirements', component: () => import('@/components/productmanager/ProductMangerClientRequirements.vue'), props: r => ({ clientId: r.params.clientId }) },
            { path: 'clients-update', name: 'ProductManagerClientsUpdate', component: () => import('@/components/productmanager/ProductMangerClientUpdate.vue') },
            { path: 'clients-update/:id', name: 'ProductManagerClientsUpdateDetails', component: () => import('@/components/productmanager/ProductMangerUpdateClient.vue'), props: r => ({ clientID: r.params.id }) },
            { path: 'projects', name: 'ProductManagerProjects', component: () => import('@/components/productmanager/ProductMangerProjects.vue') },
            { path: 'performance', name: 'ProductManagerPerformance', component: () => import('@/components/productmanager/ProductMangerPerformance.vue') },
            { path: 'performance/:id', name: 'ProductManagerPerformanceDetails', component: () => import('@/components/productmanager/ProductMangerEmployeePerformance.vue'), props: r => ({ employeeId: r.params.id }) },
        ],
    },
    
    {
        path: '/hr',
        component: () => import('@/components/hr/HRLayout.vue'),
        meta: { requiresHRAuth: true },
        children: [
            { path: 'dashboard', name: 'HRDashboard', component: () => import('@/components/hr/HRDashboard.vue') },
            { path: 'chatbot', name: 'HRChatbot', component: () => import('@/components/hr/HRChatbot.vue') },
            { path: 'employees', name: 'HREmployees', component: () => import('@/components/hr/HREmployees.vue') },
            { path: 'hrpolicies', name: 'HRPolicies', component: () => import('@/components/hr/HRPolicies.vue') },
            { path: 'projects', name: 'HRProjects', component: () => import('@/components/hr/HRProjects.vue') },
        ],
    },
];

const router = createRouter({
    history: createWebHistory(process.env.BASE_URL),
    routes
});

// ✅ FINAL WORKING HR AUTH GUARD
router.beforeEach((to, from, next) => {
    const hrToken = localStorage.getItem("hr_token");

    if (to.matched.some(record => record.meta.requiresHRAuth)) {
        if (!hrToken) {
            alert("Please log in to access HR dashboard.");
            return next("/login");
        }
    }

    next();
});

export default router;

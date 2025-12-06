<template>
  <div>
    <div class="card border-0 shadow-sm rounded-4">
      <div class="card-body p-0">
        <p class="p-4 mb-0 text-secondary border-bottom">
          A live-tailing log viewer (e.g., for application, system, or audit logs) would go here.
        </p>
        <div class="table-responsive">
          <table class="table table-hover align-middle mb-0">
            <thead class="bg-light text-secondary">
              <tr>
                <th class="py-3 ps-4 border-0">Admin ID</th>
                <th class="py-3 border-0">Admin Email</th>
                <th class="py-3 border-0">Admin Name</th>
                <th class="py-3 border-0">User Count</th>
                <th class="py-3 border-0">Logs Count</th>
                <th class="py-3 pe-4 border-0">Backup Count</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td class="ps-4 fw-medium text-dark">{{ currentAdminID }}</td>
                <td class="text-secondary">{{ currentAdminEmail }}</td>
                <td class="fw-medium text-dark">{{ currentAdminName }}</td>
                <td><span class="badge bg-light text-dark border fw-normal">{{ logs.userCount }}</span></td>
                <td><span class="badge bg-light text-dark border fw-normal">{{ logs.logsCount }}</span></td>
                <td class="pe-4"><span class="badge bg-light text-dark border fw-normal">{{ logs.backupsCount }}</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { make_getrequest } from '@/store/appState';
import { useNotify } from '@/utils/useNotify';

export default {
  name: 'AdminLogs',
  data() {
    return {
      logs: [],
      currentAdminID: null,
      currentAdminEmail: null,
      currentAdminName: null,
    };
  },
  methods: {
    async fetchLogs() {
      try {
        const data = await make_getrequest('/api/admin/summary');
        this.logs = data;
        this.currentAdminID = this.logs.currentAdmin.id;
        this.currentAdminEmail = this.logs.currentAdmin.email;
        this.currentAdminName = this.logs.currentAdmin.name;
      } catch (error) {
        console.error('Failed to fetch logs', error);
      }
    },
  },
  mounted() {
    const user = JSON.parse(localStorage.getItem('user'));
    if (!localStorage.getItem('token') || user.role !== 'root') {
      useNotify().warn('Please login to access the admin dashboard.');
      this.$router.push('/login');
      return;
    }
    this.fetchLogs();
  },
};
</script>
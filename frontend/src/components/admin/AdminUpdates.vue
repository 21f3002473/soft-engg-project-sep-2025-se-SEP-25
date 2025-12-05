<template>
  <div>
    <div class="card border-0 shadow-sm rounded-4">
      <div class="card-body p-0">
        <p class="p-4 mb-0 text-secondary border-bottom">
          Software update status, package versions, and a "Check for Updates" button.
        </p>

        <div class="table-responsive">
          <table v-if="adminUpdatesData" class="table table-hover align-middle mb-0">
            <thead class="bg-light text-secondary">
              <tr>
                <th class="py-3 ps-4 border-0" scope="col">Current Version</th>
                <th class="py-3 border-0" scope="col">Last Checked</th>
                <th class="py-3 pe-4 border-0" scope="col">Update Available?</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td class="ps-4 fw-medium text-dark">{{ adminUpdatesData.currentVersion }}</td>
                <td class="text-secondary">{{ formatDate(adminUpdatesData.lastChecked) }}</td>
                <td class="pe-4">
                  <span class="badge rounded-pill px-3 py-2" :class="{
                    'bg-success-subtle text-success border border-success-subtle': adminUpdatesData.updateAvailable === true,
                    'bg-secondary-subtle text-secondary border border-secondary-subtle': adminUpdatesData.updateAvailable === false
                  }">
                    {{ adminUpdatesData.updateAvailable ? "Yes" : "No" }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>

          <div v-else class="text-center py-5 text-muted">
            No update records found.
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { make_getrequest } from '@/store/appState';
import { useNotify } from '@/utils/useNotify';

export default {
  name: 'AdminUpdates',
  data() {
    return {
      adminUpdatesData: null,
    };
  },
  methods: {
    async adminUpdates() {
      try {
        const data = await make_getrequest('/api/admin/updates');
        this.adminUpdatesData = data;
      } catch (error) {
        console.error('Failed to fetch admin updates', error);
      }
    },
    formatDate(dateStr) {
      return new Date(dateStr).toLocaleString();
    },
  },
  mounted() {
    const user = JSON.parse(localStorage.getItem('user'));
    if (!localStorage.getItem('token') || user.role !== 'root') {
      useNotify().warn('Please login to access the admin dashboard.');
      this.$router.push('/login');
      return;
    }
    this.adminUpdates();
  },
};
</script>
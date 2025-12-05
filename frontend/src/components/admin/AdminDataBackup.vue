<template>
  <div>
    <div v-if="oldBackupConfig" class="card border-0 shadow-sm rounded-4 mb-4">
      <div class="card-header bg-white py-3 px-4 border-bottom-0">
        <h2 class="h5 fw-bold mb-0 text-dark">Current Backup Details</h2>
      </div>
      <div class="card-body p-0">
        <div class="table-responsive">
          <table class="table table-hover align-middle mb-0">
            <thead class="bg-light text-secondary">
              <tr>
                <th class="py-3 ps-4 border-0">Day</th>
                <th class="py-3 border-0">Backup Type</th>
                <th class="py-3 pe-4 border-0">DateTime</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="backup in oldBackupConfig" :key="backup.id">
                <td class="ps-4 fw-medium text-dark">{{ backup.day }}</td>
                <td>
                  <span class="badge bg-light text-dark border fw-normal">{{ prettyType(backup.type) }}</span>
                </td>
                <td class="pe-4 text-secondary">{{ formattedDatetime(backup.datetime) }}</td>
              </tr>
              <tr v-if="oldBackupConfig.length === 0">
                <td colspan="3" class="text-center py-4 text-muted">No backup configurations found.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <div class="card border-0 shadow-sm rounded-4">
      <div class="card-header bg-white py-3 px-4 border-bottom-0">
        <h2 class="h5 fw-bold mb-0 text-dark">Take New Backup</h2>
      </div>
      <div class="card-body p-4">
        <div class="row g-3 align-items-end">
          <div class="col-md-4">
            <label class="form-label fw-medium small text-secondary">Day</label>
            <select v-model="day" class="form-select bg-light border-0" required>
              <option disabled value="">Select day</option>
              <option v-for="w in weekdays" :key="w" :value="w">{{ w }}</option>
            </select>
          </div>
          <div class="col-md-4">
            <label class="form-label fw-medium small text-secondary">Backup Type</label>
            <select v-model="backup_type" class="form-select bg-light border-0" required>
              <option value="">Select Backup Type</option>
              <option value="FULL">Full Backup</option>
              <option value="INCREMENTAL">Incremental</option>
              <option value="DIFFERENTIAL">Differential</option>
            </select>
          </div>
          <div class="col-md-4">
            <label class="form-label fw-medium small text-secondary">Date & Time</label>
            <input type="datetime-local" required v-model="date_time" class="form-control bg-light border-0" />
          </div>
        </div>
        <div class="d-flex justify-content-end mt-4">
          <button class="btn btn-primary px-5 py-2 fw-semibold shadow-sm" @click="saveConfig">
            Take Backup
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { make_getrequest, make_putrequest } from '@/store/appState';

export default {
  name: 'AdminDataBackup',
  props: {
    title: {
      type: String,
      default: 'Data Backup'
    }
  },
  data() {
    return {
      backups: [],
      day: '',
      backup_type: '',
      date_time: '',
      datetimeLocal: '',
      weekdays: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
      oldBackupConfig: null
    };
  },
  methods: {
    async fetchBackups() {
      try {
        const data = await make_getrequest('/api/admin/backup-config');
        this.oldBackupConfig = data || [];
      } catch (err) {
        console.error('Error fetching backups:', err);
        this.oldBackupConfig = [];
      }
    },
    async saveConfig() {
      if (!this.day) { alert('Pick a day'); return; }
      if (!this.backup_type) { alert('Pick a backup type'); return; }

      let isoDatetime = null;
      if (this.date_time) {
        const d = new Date(this.date_time);
        if (isNaN(d)) {
          alert('Please choose a valid date and time.');
          return;
        }
        isoDatetime = d.toISOString();
      } else {
        alert('Please choose a valid date and time.');
        return;
      }

      const newBackupItem = {
        id: this.backups.length + 1,
        day: this.day,
        type: this.backup_type.toLocaleLowerCase(),
        datetime: isoDatetime
      };

      const currentList = this.backups.map(b => ({
        day: b.day,
        type: b.type,
        datetime: b.datetime
      }));

      const fullPayloadList = [...currentList, newBackupItem];
      const payload = { backups: fullPayloadList };

      try {
        await make_putrequest('/api/admin/backup-config', payload);
        alert('Saved successfully');

        this.day = '';
        this.backup_type = '';
        this.date_time = '';

        await this.fetchBackups();

      } catch (e) {
        console.error(e);
        alert(e.message || 'Save failed');
      }
    },

    prettyType(type) {
      if (!type) return '—';
      if (type === 'full') return 'Full Backup';
      if (type === 'incremental') return 'Incremental';
      if (type === 'differential') return 'Differential';
      return type;
    },

    formattedDatetime(dt) {
      if (!dt) return 'Not scheduled';
      try {
        const d = new Date(dt);
        if (isNaN(d)) return dt;
        return d.toLocaleString();
      } catch (e) {
        return dt;
      }
    },

    runBackup(item) {
      if (!item) return;
      console.log('Triggering backup for', item.day, item);

      if (typeof item.status === 'undefined') item.status = null;
      if (typeof item.lastRunAt === 'undefined') item.lastRunAt = null;

      item.status = 'Running';

      setTimeout(() => {
        const ok = Math.random() > 0.15;
        if (ok) {
          item.status = 'Success';
          item.lastRunAt = new Date().toISOString();
          console.log(`Backup success for ${item.day}`);
        } else {
          item.status = 'Failed';
          console.error(`Backup failed for ${item.day}`);
        }
      }, 1200);
    },

    downloadLatest(item) {
      console.log('Download latest backup for', item.day);
      alert(`Pretend downloading latest backup for ${item.day} — implement server endpoint to return file.`);
    },

    saveSingleConfig(item) {
      console.log('Saving single config for', item.day, item);
      alert(`Saved config for ${item.day} (UI only). Implement API call in saveSingleConfig()`);
    },

    resetToDefaults() {
      if (!confirm('Reset all backup schedules to default empty state?')) return;
      this.backups = [];
    }
  },
  mounted() {
    const user = JSON.parse(localStorage.getItem('user'));
    if (!localStorage.getItem('token') || user.role !== 'root') {
      alert('Please login to access the admin dashboard.');
      this.$router.push('/login');
      return;
    }
    this.fetchBackups();
  }
};
</script>
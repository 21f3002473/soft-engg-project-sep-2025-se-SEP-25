<template>
  <div class="dashboard">

    <main class="dashboard-content">
      
      <h1>Backups</h1>

      <!-- ===== Actions Table ===== -->
      <table class="table table-striped table-hover table-bordered shadow-sm custom-table align-middle">
        <thead class="table-dark">
          <tr>
            <th>Day</th>
            <th>Backup Type</th>
            <th>DateTime</th>
          </tr>
        </thead>
        <tbody>
            <tr>
              <td>
                <select v-model="day" class="" required>
                  <option v-for="w in weekdays" :key="w" :value="w">{{ w }}</option>
                </select>
              </td>
              <td>
                <select v-model="backup_type" class="" required>
                  <option value="">Select Backup Type</option>
                  <option value="FULL">Full Backup</option>
                  <option value="INCREMENTAL">Incremental</option>
                  <option value="DIFFERENTIAL">Differential</option>
                </select>
              </td>
              <td>
                <input type="datetime-local" required v-model="date_time" class="backup-datetime" />
              </td>
            </tr>
        </tbody>
      </table>
        <!-- Global actions -->
        <div class="d-flex justify-content-end gap-2 mt-2">
          <button class="btn btn-primary" @click="saveConfig">Take Backup</button>
          <button class="btn btn-outline-danger" @click="resetToDefaults">Reset</button>
        </div>
      <!-- ===== End Actions Table ===== -->
    </main>

    <div v-if="oldBackupConfig && oldBackupConfig.length">
      <h2>Backup History</h2>
      <table class="table table-striped table-hover table-bordered shadow-sm custom-table align-middle">
        <thead class="table-dark">
          <tr>
            <th>Day</th>
            <th>Backup Type</th>
            <th>DateTime</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="backup in backups" :key="backup.id">
            <td>{{ backup.day }}</td>
            <td>{{ prettyType(backup.type) }}</td>
            <td>{{ formattedDatetime(backup.datetime) }}</td>
          </tr>
        </tbody>
      </table>
    </div>

  </div>
</template>

<script>
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
      // Always ensure backups starts as an array
      backups: [],
      day: '',
      backup_type: '',
      date_time: '',
      datetimeLocal: '',
      weekdays: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
      oldBackupConfig: null // to track changes
    };
  },
  methods: {
    // Fetch existing backup config from API
    async fetchBackups() {
      // Logic to fetch existing backup config from API
      console.log('Fetching backup config...');
      try {
        const res = await fetch(`http://localhost:8000/api/admin/backup-config`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${localStorage.getItem('token')}`
          },
        });

        if (!res.ok) {
          console.error('Failed to fetch backup config, status:', res.status);
          // keep existing this.backups (safe) or set to empty array
          return;
        }

        const data = await res.json();
        console.log('Backup config data:', data);
        this.backups = data || [];
      } catch (err) {
        console.error('Error fetching backups:', err);
        // fallback to an empty array — prevents template render crash
        this.oldBackupConfig = this.oldBackupConfig || [];
      }
    },
    // Save entire backup config
    async saveConfig() {
      // 1. Validation
      if (!this.day) { alert('Pick a day'); return; }
      if (!this.backup_type) { alert('Pick a backup type'); return; }

      // 2. Date Parsing — only use date_time (the bound field)
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
      console.log(this.backups.length + 1, this.day, this.backup_type.toLocaleLowerCase(), isoDatetime);

      const newBackupItem = {
        id: this.backups.length + 1,
        day: this.day,
        type: this.backup_type.toLocaleLowerCase(),
        datetime: isoDatetime
      };

      // Merge with existing backups so history isn’t wiped
      const currentList = this.backups.map(b => ({
        day: b.day,
        type: b.type,
        datetime: b.datetime
      }));

      const fullPayloadList = [...currentList, newBackupItem];
      const payload = { backups: fullPayloadList };

      console.log('Sending payload:', payload);

      try {
        const res = await fetch('http://localhost:8000/api/admin/backup-config', {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${localStorage.getItem('token')}`
          },
          body: JSON.stringify(payload)
        });

        if (!res.ok) {
            const errText = await res.text();
            throw new Error(`Save failed: ${res.status} - ${errText}`);
        }

        alert('Saved successfully');
        
        // Clear inputs
        this.day = '';
        this.backup_type = '';
        this.date_time = '';

        // Refresh list
        await this.fetchBackups();
        
      } catch (e) {
        console.error(e);
        alert(e.message || 'Save failed');
      }
    },

    /* ---------------- New helper methods for actions table ---------------- */

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
      // Guard
      if (!item) return;
      console.log('Triggering backup for', item.day, item);

      // Ensure fields exist (we normalized them on fetch but be safe)
      if (typeof item.status === 'undefined') item.status = null;
      if (typeof item.lastRunAt === 'undefined') item.lastRunAt = null;

      // Use direct assignments (Vue 3 reacts to these if props exist on object)
      item.status = 'Running';

      // Simulated API call — replace with real API call
      setTimeout(() => {
        const ok = Math.random() > 0.15; // simulated outcome
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
    // fetch existing backup config
    const user = JSON.parse(localStorage.getItem('user'));
    if(!localStorage.getItem('token') || user.role !== 'root') {
      alert('Please login to access the admin dashboard.');
      this.$router.push('/login');
      return;
    }
    this.fetchBackups();
  }
};
</script>

<style scoped>
.dashboard {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  background-color: #f4f7f6;
  height: 100vh;
  color: #333;
}

a {
  text-decoration: none;
  color: #555;
  font-size: 14px;
}

a:hover {
  color: #000;
}

/* Style for the active router link */
.router-link-exact-active {
  color: #007bff;
  font-weight: bold;
}

/* 1. Header Navigation (Copied) */
.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 30px;
  background-color: #ffffff;
  border-bottom: 1px solid #ddd;
}

.nav-links a {
  margin-right: 25px;
}

.account-link a {
  font-weight: bold;
}

/* 2. Main Content Area (Copied) */
.dashboard-content {
  padding: 25px 30px;
}

/* 2a. Content Header */
.dashboard-content h1 {
  margin: 0;
  font-size: 28px;
  font-weight: 600;
  margin-bottom: 20px;
}

/* 2b. New Styles for Backup List */
.backup-container {
  background-color: #ffffff;
  border: 1px solid #ddd;
  border-radius: 8px;
  max-height: 75vh;
  overflow-y: auto;
}

.backup-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 15px;
  padding: 15px 20px;
  border-bottom: 1px solid #eee;
}

.backup-item:last-child {
  border-bottom: none;
}

.day-label {
  font-weight: 600;
  flex-basis: 20%; 
}

.inputs-group {
  display: flex;
  gap: 15px;
  flex-grow: 1; 
  justify-content: flex-end; 
}

.backup-select,
.backup-datetime {
  padding: 8px 12px;
  border: 1px solid #ccc;
  border-radius: 4px;
  background-color: #f9f9f9;
  font-size: 14px;
  font-family: inherit;
  min-width: 200px;
}
.backup-table {
  border-radius: 10px;
  overflow: hidden; 
  background: #fff;
}

.backup-table td, .backup-table th {
  vertical-align: middle !important;
}

/* ================= New styles for the actions table (matches existing aesthetic) ================= */

.action-table {
  border-radius: 10px;
  overflow: hidden;
  background: #fff;
  margin-bottom: 8px;
}

.action-table th,
.action-table td {
  vertical-align: middle !important;
  padding: 10px 12px;
  font-size: 14px;
}

/* Status badges to mirror simple neutral -> success -> fail look */
.status-badge {
  display: inline-block;
  padding: 6px 10px;
  border-radius: 999px;
  font-size: 13px;
  font-weight: 600;
  min-width: 70px;
  text-align: center;
}

.status-idle {
  background: #f1f3f5;
  color: #495057;
}

.status-running {
  background: linear-gradient(90deg, #fff3cd, #ffe8a1);
  color: #7a5b00;
  box-shadow: 0 0 6px rgba(255, 200, 0, 0.08);
}

.status-success {
  background: #e6f4ea;
  color: #0f5132;
  border: 1px solid rgba(15,81,50,0.08);
}

.status-failed {
  background: #fdecea;
  color: #7a1a1a;
  border: 1px solid rgba(122,26,26,0.06);
}

/* small responsive tweaks */
@media (max-width: 720px) {
  .backup-table thead th,
  .action-table thead th {
    font-size: 13px;
  }
  .action-table td {
    font-size: 13px;
  }
  .backup-content-cta {
    flex-direction: column;
    gap: 8px;
  }
}

/* minor spacing adjustments to fit the project aesthetic */
.backup-actions-section h2 {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 8px;
}

/* buttons gap helper (bootstrap has gap utilities but keep style self-contained) */
.d-flex.gap-2 {
  gap: 8px;
}
</style>

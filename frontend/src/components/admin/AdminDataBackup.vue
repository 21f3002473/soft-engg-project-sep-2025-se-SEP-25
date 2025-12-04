<template>
  <div class="dashboard">

    <main class="dashboard-content">
      
      <h1>Backups</h1>

      <table v-if="backups && backups.length" class="table table-striped table-hover table-bordered align-middle backup-table">
        <thead class="table-dark">
          <tr>
            <th style="width: 120px;">Day</th>
            <th style="width: 200px;">Backup Type</th>
            <th>Date & Time</th>
          </tr>
        </thead>

        <tbody>
          <tr v-for="item in backups" :key="item.day">
            <!-- Day -->
            <td class="fw-bold">{{ item.day }}</td>

            <!-- Backup Type -->
            <td>
              <select v-model="item.type" class="form-select">
                <option value="" disabled>Select Backup Type</option>
                <option value="full">Full Backup</option>
                <option value="incremental">Incremental Backup</option>
                <option value="differential">Differential Backup</option>
              </select>
            </td>

            <!-- Datetime -->
            <td>
              <input 
                type="datetime-local" 
                v-model="item.datetime" 
                class="form-control"
              />
            </td>
          </tr>
        </tbody>
      </table>

      <!-- ===== New Actions Table: Take Backup / Status / Run ===== -->
      <section class="mt-4 backup-actions-section">
        <h2 class="mt-3 mb-2">Take Backup — Actions</h2>

        <table class="table table-sm table-hover table-bordered align-middle action-table">
          <thead class="table-secondary">
            <tr>
              <th style="width: 120px;">Day</th>
              <th style="width: 200px;">Type</th>
              <th>Scheduled (Local)</th>
              <th style="width: 140px;">Status</th>
              <th style="width: 200px;">Actions</th>
            </tr>
          </thead>

          <tbody>
            <tr v-for="item in backups" :key="`action-${item.day}`">
              <td class="fw-bold">{{ item.day }}</td>
              <td>{{ prettyType(item.type) }}</td>
              <td>{{ formattedDatetime(item.datetime) }}</td>
              <td>
                <span 
                  class="status-badge"
                  :class="{
                    'status-idle': !item.status || item.status === 'Idle',
                    'status-running': item.status === 'Running',
                    'status-success': item.status === 'Success',
                    'status-failed': item.status === 'Failed'
                  }"
                >
                  {{ item.status || 'Idle' }}
                </span>
              </td>
              <td>
                <div class="d-flex gap-2">
                  <button
                    class="btn btn-sm btn-outline-primary"
                    :disabled="item.status === 'Running'"
                    @click="runBackup(item)"
                  >
                    Run Now
                  </button>

                  <button
                    class="btn btn-sm btn-outline-secondary"
                    @click="downloadLatest(item)"
                  >
                    Download
                  </button>

                  <button
                    class="btn btn-sm btn-outline-success"
                    @click="saveSingleConfig(item)"
                  >
                    Save
                  </button>
                </div>
              </td>
            </tr>

            <!-- If no backups configured show helpful CTA row -->
            <tr v-if="!backups || backups.length === 0">
              <td colspan="5" class="text-center py-4">
                No backup schedule configured yet. Configure the days above, set types and schedule, then press Save.
              </td>
            </tr>
          </tbody>
        </table>

        <!-- Global actions -->
        <div class="d-flex justify-content-end gap-2 mt-2">
          <button class="btn btn-primary" @click="saveConfig">Save All Config</button>
          <button class="btn btn-outline-danger" @click="resetToDefaults">Reset</button>
        </div>
      </section>
      <!-- ===== End Actions Table ===== -->

    </main>
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
      backups: [
        // defaults commented out for sample:
        // { day: 'Monday', type: 'full', datetime: '2025-10-30T03:00', status: null, lastRunAt: null },
      ]
    };
  },
  methods: {
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

        // Defensive: ensure backups is always an array and every entry has required reactive fields
        const raw = (data && Array.isArray(data.backups)) ? data.backups : [];
        this.backups = raw.map(entry => ({
          day: entry.day ?? 'Unnamed',
          type: entry.type ?? '',
          datetime: entry.datetime ?? '',
          // ensure reactive properties exist
          status: entry.status ?? null,
          lastRunAt: entry.lastRunAt ?? null
        }));
      } catch (err) {
        console.error('Error fetching backups:', err);
        // fallback to an empty array — prevents template render crash
        this.backups = this.backups || [];
      }
    },
    async saveConfig() {
      console.log('Saving backup config:', this.backups);
      try {
        const res = await fetch('http://localhost:8000/api/admin/backup-config', {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${localStorage.getItem('token')}` },
          body: JSON.stringify({ backups: this.backups })
        });
        if (!res.ok) {
          throw new Error('Save failed');
        }
        alert('Saved successfully');
      } catch (e) {
        console.error(e);
        alert('Save failed');
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

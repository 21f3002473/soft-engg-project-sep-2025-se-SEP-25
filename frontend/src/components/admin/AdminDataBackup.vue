<template>
  <div class="dashboard">
    <!-- <header class="dashboard-header">
      <div class="nav-links">
        <router-link to="/admin/dashboard">Home</router-link>
        <router-link to="/systemStatus">System Status</router-link>
        <router-link to="/logs">Logs</router-link>
        <router-link to="/updates">Updates</router-link>
        <router-link to="/admin/dashboard/backups" class="router-link-exact-active">Backups</router-link>
      </div>
      <div class="account-link">
        <router-link to="/account">Account</router-link>
      </div>
    </header> -->

    <main class="dashboard-content">
      
      <h1>Backups</h1>

      <div class="backup-container">
        <div class="backup-item" v-for="item in backups" :key="item.day">
          <span class="day-label">{{ item.day }}</span>
          
          <div class="inputs-group">
            <select v-model="item.type" class="backup-select">
              <option value="" disabled>BackUp Type</option>
              <option value="full">Full Backup</option>
              <option value="incremental">Incremental Backup</option>
              <option value="differential">Differential Backup</option>
            </select>
            
            <input type="datetime-local" v-model="item.datetime" class="backup-datetime" />
          </div>
        </div>
      </div>

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
      // Data to populate the v-for loop
      backups: [
        { day: 'Monday', type: 'full', datetime: '2025-10-30T03:00' },
        { day: 'Tuesday', type: 'incremental', datetime: '2025-10-31T03:00' },
        { day: 'Wednesday', type: 'incremental', datetime: '2025-11-01T03:00' },
        { day: 'Thursday', type: 'incremental', datetime: '2025-11-02T03:00' },
        { day: 'Friday', type: 'full', datetime: '2025-11-03T03:00' }
      ]
    };
  },
  methods: {
    saveConfig() {
      console.log('Saving backup config:', this.backups);

      // API call to POST/PUT this.backups would go here
    }
  },
  mounted() {
    // Code to run when the component is mounted
    // e.g., fetch existing backup config
    console.log('Fetching backup config...');
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
</style>
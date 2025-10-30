<template>
  <div class="dashboard">
    <header class="dashboard-header">
      <div class="nav-links">
        <router-link to="/systemStatus">System Status</router-link>
        <router-link to="/logs">Logs</router-link>
        <router-link to="/updates">Updates</router-link>
        <router-link to="/backups">Backups</router-link>
      </div>
      <div class="account-link">
        <router-link to="/account">Account</router-link>
      </div>
    </header>

    <main class="dashboard-content">
      <div class="content-header">
        <h1>{{ title }}</h1>
        <div class="search-bar">
          <input type="text" placeholder="Search" />
          </div>
      </div>

      <div class="main-area">
        
        <div class="employee-list">
          <div class="employee-item" v-for="emp in employees" :key="emp.id">
            <span class="emp-name">{{ emp.name }}</span>
            <span class="emp-status" :class="emp.status.toLowerCase().replace('!', '')">
              {{ emp.status }}
            </span>
            <button class="btn" @click="changeStatus">Change Status</button>
            <select class="status-dropdown">
              <option value="">Status Change Dropdown</option>
              <option value="active">Set Active</option>
              <option value="pending">Set Pending</option>
              <option value="disabled">Set Disabled</option>
            </select>
          </div>
        </div>

        <div class="chatbot-area">
            <aside class="chatbot-panel">
                <template v-if="isChatbotOpen">
                    <h3>Hello I am AI</h3>
                    <div class="chat-history">
                    <textarea name="textquery" id="textquery" rows="10">
                    Chat history will appear here...
                    </textarea>
                    </div>
                </template>
                <button @click="isChatbotOpen = !isChatbotOpen" class="btn btn-ai">AI</button>
            </aside>
        </div>

      </div>
    </main>
  </div>
</template>

<script>
export default {
  name: 'AdminDashboard',
  data() {
    return {
      title: 'Super Admin Dashboard',
      // Dummy data to populate the v-for loop
      employees: [
        { id: 1, name: 'EMP1', status: 'New!' },
        { id: 2, name: 'EMP2', status: 'Old' },
        { id: 3, name: 'EMP3', status: 'New!' },
        { id: 4, name: 'EMP4', status: 'New!' },
        { id: 5, name: 'EMP5', status: 'New!' },
        { id: 6, name: 'EMP6', status: 'New!' }
      ],
      isChatbotOpen: false,
    };
  },
  methods: {
    async fetchData() {
      console.log('Fetching data...');
      // API call would go here
    },
    changeStatus() {
      console.log('Change status');
      // Logic to change status would go here
    },
  },
  mounted() {
    // Code to run when the component is mounted
    this.fetchData();
  }
};
</script>

<style scoped>
/* Resets and Basic Styles */
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

.btn {
  padding: 8px 12px;
  border: 1px solid #ccc;
  border-radius: 4px;
  background-color: #f9f9f9;
  cursor: pointer;
  font-size: 14px;
}

.btn:hover {
  background-color: #eee;
}

/* 1. Header Navigation */
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

/* 2. Main Content Area */
.dashboard-content {
  padding: 25px 30px;
}

/* 2a. Content Header (Title + Search) */
.content-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.content-header h1 {
  margin: 0;
  font-size: 28px;
  font-weight: 600;
}

.search-bar input {
  padding: 8px 12px;
  border: 1px solid #ccc;
  border-radius: 4px;
  min-width: 250px; /* Give it some size */
}

/* 2b. Main Area (List + Chat) */
.main-area {
  display: flex;
  gap: 25px; /* Space between list and chatbot */
}

/* Employee List (Left) */
.employee-list {
  flex: 3; /* Takes up 3/4 of the space */
  background-color: #ffffff;
  border: 1px solid #ddd;
  border-radius: 8px;
}

.employee-item {
  display: flex;
  align-items: center;
  gap: 15px; /* Space between items in a row */
  padding: 15px 20px;
  border-bottom: 1px solid #eee;
}

.employee-item:last-child {
  border-bottom: none;
}

.emp-name {
  font-weight: 600;
  flex-basis: 10%; /* Allocates space for the name */
}

.emp-status {
  flex-basis: 10%;
  text-align: center;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.emp-status.new {
  background-color: #e0f8e0;
  color: #006400;
}

.emp-status.old {
  background-color: #eee;
  color: #555;
}

.status-dropdown {
  padding: 8px 12px;
  border: 1px solid #ccc;
  border-radius: 4px;
  background-color: #f9f9f9;
  flex-grow: 1; /* Takes up remaining space */
}

/* Chatbot Panel (Right) */
.chatbot-panel {
  flex: 1; /* Takes up 1/4 of the space */
  background-color: #ffffff;
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 20px;
  display: flex;
  flex-direction: column;
}

.chatbot-panel h3 {
  margin-top: 0;
  margin-bottom: 15px;
  text-align: center;
  font-weight: 600;
}

.chat-history {
  flex-grow: 1; /* Makes the chat box fill vertical space */
  border: 1px solid #eee;
  border-radius: 4px;
  padding: 10px;
  margin-bottom: 15px;
  min-height: 250px; /* Ensures it has a good height */
  font-family: monospace;
  color: #666;
  overflow-y: auto; /* Adds scroll if content is long */
}

/* THIS IS THE MODIFIED RULE */
.btn-ai {
  background-color: #ececec;
  border: none;
  border-radius: 50%; /* Makes it a circle */
  width: 50px;
  height: 50px;
  font-weight: bold;
  align-self: center; /* <<< CHANGED FROM flex-end */
  margin-top: auto; /* Keeps it at the bottom */
}
</style>
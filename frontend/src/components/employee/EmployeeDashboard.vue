<template>
  <div class="dashboard-page">
    <section class="welcome-section">
      <div class="welcome-card">
        <h2>Welcome back, <span class="highlight">{{ userName }}</span></h2>
        <p>Here’s what’s happening in your workspace today.</p>
      </div>
    </section>

    <section class="stats-section">
      <div class="stat-card" v-for="(item, index) in stats" :key="index">
        <div class="stat-icon" :class="item.colorClass">
          <i :class="item.icon"></i>
        </div>
        <div class="stat-info">
          <h3>{{ item.value }}</h3>
          <p>{{ item.label }}</p>
        </div>
      </div>
    </section>

    <section class="content-section">
      <div class="tasks">
        <h3>Your Tasks</h3>
        <div class="add-task-form">
          <input 
            v-model="newTask" 
            @keyup.enter="addTask"
            placeholder="Add a new task..." 
            class="task-input"
          />
          <button @click="addTask" :disabled="!newTask" class="add-btn">
            <i class="bi bi-plus"></i>
          </button>
        </div>
        <div v-if="loadingTasks">Loading tasks...</div>
        <ul v-else>
          <li v-for="task in displayedTasks" :key="task.id">
            <input 
              type="checkbox" 
              :checked="task.status === 'completed'" 
              @change="toggleTask(task)"
            />
            <span :class="{ done: task.status === 'completed' }">{{ task.task }}</span>
            <small v-if="task.deadline" class="deadline">Due: {{ formatDate(task.deadline) }}</small>
          </li>
          <li v-if="displayedTasks.length === 0">No recent tasks.</li>
        </ul>
      </div>

      <div class="announcements">
        <h3>Announcements</h3>
        <div v-if="loadingAnnouncements">Loading announcements...</div>
        <div v-else>
          <div class="announcement" v-for="item in announcements" :key="item.id">
            <h4>{{ item.announcement }}</h4>
            <p v-if="item.message">{{ item.message }}</p>
            <small>{{ formatDate(item.created_at) }}</small>
          </div>
          <div v-if="announcements.length === 0">No announcements.</div>
        </div>
      </div>
    </section>
  </div>
</template>

<script>
import { make_getrequest, make_putrequest, make_postrequest } from "@/store/appState.js";

export default {
  name: 'EmployeeDashboard',
  data() {
    return {
      userName: 'User',
      loadingTasks: false,
      loadingAnnouncements: false,
      stats: [
        { label: 'Pending Tasks', value: 0, icon: 'fas fa-tasks', colorClass: 'blue', key: 'pending_tasks' },
        { label: 'Completed', value: 0, icon: 'fas fa-check-circle', colorClass: 'green', key: 'completed_tasks' },
        { label: 'Requests', value: 0, icon: 'fas fa-envelope-open-text', colorClass: 'purple', key: 'requests' },
        { label: 'Courses Completed', value: 0, icon: 'fas fa-bell', colorClass: 'orange', key: 'courses_completed' }
      ],
      tasks: [],
      announcements: [],
      newTask: ''
    };
  },
  computed: {
    displayedTasks() {
      const pendingTasks = this.tasks
        .filter(t => t.status === 'pending')
        .sort((a, b) => new Date(a.date_created) - new Date(b.date_created)); // Oldest first

      const completedTasks = this.tasks
        .filter(t => t.status === 'completed')
        .sort((a, b) => new Date(b.date_created) - new Date(a.date_created)); // Newest first

      const limit = 8;
      const result = [];

      result.push(...pendingTasks.slice(0, limit));

      if (result.length < limit) {
        const remaining = limit - result.length;
        result.push(...completedTasks.slice(0, remaining));
      }

      return result;
    }
  },
  mounted() {
    this.fetchDashboardData();
  },
  methods: {
    async fetchDashboardData() {
      this.loadingTasks = true;
      this.loadingAnnouncements = true;
      try {
        const data = await make_getrequest('/api/employee/dashboard');
        
        if (data.user && data.user.name) {
          this.userName = data.user.name;
        }
        if (data.stats) {
          this.stats.forEach(stat => {
            if (data.stats[stat.key] !== undefined) {
              stat.value = data.stats[stat.key];
            }
          });
        }

        if (data.tasks) {
          this.tasks = data.tasks;
        }

        if (data.announcements) {
          this.announcements = data.announcements;
        }

      } catch (error) {
        console.error("Failed to fetch dashboard data:", error);
      } finally {
        this.loadingTasks = false;
        this.loadingAnnouncements = false;
      }
    },
    async addTask() {
      if (!this.newTask.trim()) return;
      
      try {
        const payload = { task: this.newTask };
        const response = await make_postrequest('/api/employee/todo', payload);
        
        this.tasks.unshift({
          id: response.task_id,
          task: this.newTask,
          status: 'pending',
          date_created: new Date().toISOString()
        });
        
        this.newTask = '';
        
        const pendingStat = this.stats.find(s => s.key === 'pending_tasks');
        if (pendingStat) pendingStat.value++;
        
      } catch (error) {
        console.error("Failed to add task:", error);
        alert("Failed to add task");
      }
    },
    async toggleTask(task) {
      const newStatus = task.status === 'completed' ? 'pending' : 'completed';
      const originalStatus = task.status;
      task.status = newStatus;

      try {
        await make_putrequest(`/api/employee/todo/${task.id}`, { status: newStatus });
        this.updateLocalStats(originalStatus, newStatus);
      } catch (error) {
        console.error("Failed to update task:", error);

        task.status = originalStatus;
        alert("Failed to update task status");
      }
    },
    updateLocalStats(oldStatus, newStatus) {
      const pendingStat = this.stats.find(s => s.key === 'pending_tasks');
      const completedStat = this.stats.find(s => s.key === 'completed_tasks');

      if (oldStatus === 'pending' && newStatus === 'completed') {
        if (pendingStat) pendingStat.value--;
        if (completedStat) completedStat.value++;
      } else if (oldStatus === 'completed' && newStatus === 'pending') {
        if (pendingStat) pendingStat.value++;
        if (completedStat) completedStat.value--;
      }
    },
    formatDate(dateString) {
      if (!dateString) return '';
      const date = new Date(dateString);
      if (isNaN(date.getTime())) return dateString;
      
      const now = new Date();
      const diffInSeconds = Math.floor((now - date) / 1000);
      
      if (diffInSeconds < 60) return 'Just now';
      if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)} mins ago`;
      if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)} hours ago`;
      if (diffInSeconds < 172800) return 'Yesterday';
      
      return date.toLocaleDateString();
    }
  }
};
</script>

<style scoped>
.dashboard-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
  font-family: "Inter", sans-serif;
  color: #1e293b;
}

.welcome-card {
  background: linear-gradient(135deg, #2563eb, #1d4ed8);
  color: #fff;
  border-radius: 16px;
  padding: 20px 24px;
  box-shadow: 0 6px 20px rgba(37, 99, 235, 0.2);
  text-align: left;
  margin-bottom: 20px;
}

.welcome-card h2 {
  font-size: 26px;
  margin-bottom: 8px;
  font-weight: 700;
}

.welcome-card .highlight {
  color: #fffacd;
}

.welcome-card p {
  font-size: 15px;
  opacity: 0.9;
}

.stats-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  background: #fff;
  border-radius: 14px;
  display: flex;
  align-items: center;
  padding: 18px 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 16px rgba(37, 99, 235, 0.2);
}

.stat-icon {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  color: white;
  font-size: 20px;
  margin-right: 14px;
}

.stat-icon.blue {
  background: #3b82f6;
}

.stat-icon.green {
  background: #10b981;
}

.stat-icon.purple {
  background: #8b5cf6;
}

.stat-icon.orange {
  background: #f59e0b;
}

.stat-info h3 {
  font-size: 22px;
  margin: 0;
  color: #1e3a8a;
}

.stat-info p {
  margin: 2px 0 0;
  color: #475569;
  font-size: 14px;
}

.content-section {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

.tasks, .announcements {
  background: #fff;
  border-radius: 14px;
  padding: 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.tasks h3, .announcements h3 {
  margin-bottom: 14px;
  font-weight: 600;
  color: #1e40af;
}

.tasks ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.tasks li {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 0;
  font-size: 15px;
  border-bottom: 1px solid #f1f5f9;
}

.tasks li:last-child {
  border-bottom: none;
}

.tasks li span.done {
  text-decoration: line-through;
  color: #94a3b8;
}

.deadline {
  margin-left: auto;
  font-size: 12px;
  color: #64748b;
  background: #f1f5f9;
  padding: 2px 6px;
  border-radius: 4px;
}

.announcement {
  margin-bottom: 16px;
  border-left: 4px solid #2563eb;
  padding-left: 12px;
}

.announcement h4 {
  margin: 0 0 4px;
  color: #1e3a8a;
  font-size: 16px;
}

.announcement p {
  margin: 0 0 4px;
  color: #475569;
  font-size: 14px;
}

.announcement small {
  color: #94a3b8;
  font-size: 13px;
}

@media (max-width: 900px) {
  .content-section {
    grid-template-columns: 1fr;
  }
}

.add-task-form {
  display: flex;
  gap: 10px;
  margin-bottom: 15px;
}

.task-input {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  outline: none;
  transition: border-color 0.2s;
}

.task-input:focus {
  border-color: #3b82f6;
}

.add-btn {
  background: #3b82f6;
  color: white;
  border: none;
  width: 36px;
  height: 36px;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s;
}

.add-btn:hover:not(:disabled) {
  background: #2563eb;
}

.add-btn:disabled {
  background: #cbd5e1;
  cursor: not-allowed;
}

</style>
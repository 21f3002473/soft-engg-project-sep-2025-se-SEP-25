<template>
  <div class="container py-4 dashboard-page">
    <section class="mb-4">
      <div class="card border-0 shadow text-white welcome-card p-4">
        <div class="card-body p-0">
          <h2 class="fw-bold mb-2 display-8">Welcome, <span class="text-warning">{{ userName }}</span></h2>
          <p class="mb-0 opacity-75 fs-6">Here’s what’s happening in your workspace today.</p>
        </div>
      </div>
    </section>

    <section class="row g-4 mb-4">
      <div class="col-md-3 col-sm-6" v-for="(item, index) in stats" :key="index">
        <div class="card border-0 shadow-sm h-100 stat-card-hover">
          <div class="card-body d-flex align-items-center p-3">
            <div class="stat-icon rounded-3 d-flex align-items-center justify-content-center me-3 text-white" :class="item.colorClass">
              <i :class="item.icon"></i>
            </div>
            <div>
              <h3 class="h4 mb-0 fw-bold text-primary fs-4">{{ item.value }}</h3>
              <p class="text-muted mb-0">{{ item.label }}</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="row g-4">
      <div class="col-md-6">
        <div class="card border-0 shadow-sm h-100">
          <div class="card-body p-4">
            <h3 class="h3 fw-bold text-primary mb-3">Your Tasks</h3>
            
            <div class="d-flex gap-2 mb-3">
              <input 
                v-model="newTask" 
                @keyup.enter="addTask"
                placeholder="Add a new task..." 
                class="form-control py-4 fs-5"
              />
              <button @click="addTask" :disabled="!newTask" class="btn btn-primary d-flex align-items-center justify-content-center px-3">
                <i class="bi bi-plus fs-5"></i>
              </button>
            </div>

            <div v-if="loadingTasks" class="text-muted">Loading tasks...</div>
            <ul v-else class="list-group list-group-flush mx-2">
              <li v-for="task in displayedTasks" :key="task.id" class="list-group-item border-0 border-bottom d-flex align-items-center py-3">
                <input 
                  class="form-check-input mt-0 fs-5"
                  type="checkbox" 
                  :checked="task.status === 'completed'" 
                  @change="toggleTask(task)"
                />
                <span :class="{ 'text-decoration-line-through text-muted': task.status === 'completed' }" class="fs-5 mx-2">{{ task.task }}</span>
              </li>
              <li v-if="displayedTasks.length === 0" class="list-group-item border-0 text-muted fs-5">No recent tasks.</li>
            </ul>
          </div>
        </div>
      </div>

      <div class="col-md-6">
        <div class="card border-0 shadow-sm h-100">
          <div class="card-body p-4">
            <h3 class="h3 fw-bold text-primary mb-3">Announcements</h3>
            <div v-if="loadingAnnouncements" class="text-muted fs-5">Loading announcements...</div>
            <div v-else>
              <div class="mb-4 border-start border-4 border-primary ps-3" v-for="item in announcements" :key="item.id">
                <h4 class="h5 text-primary mb-2 fw-bold">{{ item.announcement }}</h4>
                <p v-if="item.message" class="text-muted mb-2 fs-6">{{ item.message }}</p>
                <small class="text-secondary">{{ formatDate(item.created_at) }}</small>
              </div>
              <div v-if="announcements.length === 0" class="text-muted fs-5">No announcements.</div>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script>
import { make_getrequest, make_putrequest, make_postrequest } from "@/store/appState.js";
import { useNotify } from "@/utils/useNotify.js";

export default {
  name: 'EmployeeDashboard',
  data() {
    return {
      userName: 'User',
      loadingTasks: false,
      loadingAnnouncements: false,
      stats: [
        { label: 'Pending Tasks', value: 0, icon: 'bi bi-list-task', colorClass: 'bg-primary', key: 'pending_tasks' },
        { label: 'Completed', value: 0, icon: 'bi bi-check-circle-fill', colorClass: 'bg-success', key: 'completed_tasks' },
        { label: 'Requests', value: 0, icon: 'bi bi-envelope', colorClass: 'bg-info', key: 'requests' },
        { label: 'Courses Completed', value: 0, icon: 'bi bi-mortarboard-fill', colorClass: 'bg-warning', key: 'courses_completed' }
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
        useNotify().error("Failed to add task");
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
        useNotify().error("Failed to update task status");
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
  font-family: "Inter", sans-serif;
  color: #1e293b;
}

.welcome-card {
  background: linear-gradient(135deg, #2563eb, #1d4ed8);
}

.stat-icon {
  width: 48px;
  height: 48px;
  font-size: 20px;
}

.stat-card-hover {
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.stat-card-hover:hover {
  transform: translateY(-3px);
  box-shadow: 0 .5rem 1rem rgba(0,0,0,.15)!important;
}
</style>
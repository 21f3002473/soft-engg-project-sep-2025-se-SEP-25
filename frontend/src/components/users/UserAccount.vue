<template>
    <div class="account-page">
      <!-- Profile Section -->
      <section class="profile-section">
        <div class="profile-header">
          <div class="avatar">JD</div>
          <div class="profile-info">
            <h2>{{ user.name }}</h2>
            <p class="role">{{ user.role }}</p>
          </div>
        </div>
      </section>

      <!-- Account Details -->
      <section class="account-section">
        <h3>Account Information</h3>
        <div class="form-grid">
          <div class="form-group">
            <label>Full Name</label>
            <input type="text" v-model="user.name" />
          </div>
          <div class="form-group">
            <label>Email</label>
            <input type="email" v-model="user.email" />
          </div>
          <div class="form-group">
            <label>Phone</label>
            <input type="tel" v-model="user.phone" />
          </div>
          <div class="form-group">
            <label>Department</label>
            <input type="text" v-model="user.department" readonly />
          </div>
        </div>
      </section>

      <!-- Preferences -->
      <section class="account-section">
        <h3>Preferences</h3>
        <div class="preferences">
          <label class="checkbox">
            <input type="checkbox" v-model="preferences.emailNotifications" />
            Receive email notifications
          </label>
          <label class="checkbox">
            <input type="checkbox" v-model="preferences.twoFactorAuth" />
            Enable two-factor authentication
          </label>
        </div>
      </section>

      <!-- Actions -->
      <div class="actions">
        <button class="btn primary" @click="saveChanges">Save Changes</button>
        <button class="btn" @click="resetForm">Cancel</button>
      </div>
    </div>
</template>

<script>
import UserLayout from './UserLayout.vue';

export default {
  name: 'UserAccount',
  components: { UserLayout },
  data() {
    return {
      user: {
        name: 'John Doe',
        email: 'john.doe@company.com',
        phone: '+1 234 567 8900',
        role: 'Software Engineer',
        department: 'Engineering'
      },
      preferences: {
        emailNotifications: true,
        twoFactorAuth: false
      }
    };
  },
  methods: {
    saveChanges() {
      // Implement save functionality
      console.log('Saving changes:', { user: this.user, preferences: this.preferences });
    },
    resetForm() {
      // Implement reset functionality
      console.log('Reset form');
    }
  }
};
</script>

<style scoped>
.account-page {
  max-width: 800px;
  margin: 0 auto;
}

.profile-section {
  margin-bottom: 32px;
}

.profile-header {
  display: flex;
  align-items: center;
  gap: 20px;
}

.avatar {
  width: 80px;
  height: 80px;
  background: #4a90e2;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 24px;
}

.profile-info h2 {
  margin: 0;
  font-size: 24px;
}

.role {
  color: #666;
  margin: 4px 0;
}

.account-section {
  background: white;
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 24px;
}

.account-section h3 {
  margin: 0 0 16px 0;
  font-size: 18px;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-weight: 500;
  color: #555;
}

.form-group input {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.preferences {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.checkbox {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
}

.btn {
  padding: 8px 16px;
  border-radius: 6px;
  border: 1px solid #ddd;
  background: white;
  cursor: pointer;
}

.btn.primary {
  background: #4a90e2;
  color: white;
  border-color: #4a90e2;
}

.btn:hover {
  opacity: 0.9;
}
</style>

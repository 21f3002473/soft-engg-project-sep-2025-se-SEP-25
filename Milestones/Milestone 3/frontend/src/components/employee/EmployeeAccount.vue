<template>
  <div class="account-page">
    <section class="profile-section">
      <div class="profile-header">
        <div class="avatar">{{ userInitials }}</div>
        <div class="profile-info">
          <h2>{{ user.name }}</h2>
          <p class="role">{{ user.role }}</p>
          <p class="department">{{ user.department }}</p>
        </div>
      </div>
    </section>

    <section class="account-section">
      <div class="section-header">
        <h3>Account Information</h3>
        <button class="btn small" @click="resetForm">Reset</button>
      </div>
      <div class="form-grid">
        <div class="form-group" v-for="(value, key) in editableFields" :key="key">
          <label :for="key">{{ keyLabels[key] }}</label>
          <input
            :id="key"
            v-model="user[key]"
            :readonly="key === 'department'"
            :type="inputTypes[key]"
          />
        </div>
      </div>
    </section>

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

    <div class="actions spaced">
      <button class="btn primary" @click="updateProfile">Update</button>
      <router-link :to="{ name: 'Login' }"><button class="btn danger" >Logout</button></router-link>
    </div>
  </div>
</template>

<script>
export default {
  name: "EmployeeAccount",
  data() {
    return {
      user: {
        name: "John Doe",
        email: "john.doe@company.com",
        phone: "+1 234 567 8900",
        role: "Software Engineer",
        department: "Engineering",
      },
      originalUser: {},
      preferences: {
        emailNotifications: true,
        twoFactorAuth: false,
      },
      keyLabels: {
        name: "Full Name",
        email: "Email",
        phone: "Phone",
        department: "Department",
      },
      inputTypes: {
        name: "text",
        email: "email",
        phone: "tel",
        department: "text",
      },
    };
  },
  computed: {
    editableFields() {
      return Object.keys(this.user)
        .filter((key) => key !== "role")
        .reduce((acc, key) => ((acc[key] = this.user[key]), acc), {});
    },
    userInitials() {
      return this.user.name
        .split(" ")
        .map((n) => n[0])
        .join("")
        .toUpperCase()
        .slice(0, 2);
    },
  },
  mounted() {
    this.originalUser = JSON.parse(JSON.stringify(this.user));
  },
  methods: {
    updateProfile() {
      console.log("Profile updated:", {
        user: this.user,
        preferences: this.preferences,
      });
      alert("Profile updated successfully!");
    },
    resetForm() {
      if (confirm("Reset all changes?")) {
        this.user = JSON.parse(JSON.stringify(this.originalUser));
      }
    },
  },
};
</script>

<style scoped>
.account-page {
  max-width: 850px;
  margin: 0 auto;
  padding: 30px 20px;
  display: flex;
  flex-direction: column;
  gap: 28px;
  background: #fafafa;
}

.profile-section {
  background: #ffffff;
  padding: 20px 24px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  border: 1px solid #e3e3e3;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.profile-header {
  display: flex;
  align-items: center;
  gap: 20px;
}

.avatar {
  width: 90px;
  height: 90px;
  border-radius: 50%;
  background: linear-gradient(135deg, #007bff, #0056d2);
  color: #fff;
  font-weight: 600;
  font-size: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.profile-info h2 {
  margin: 0;
  font-size: 24px;
  color: #222;
}

.role {
  font-weight: 500;
  color: #555;
}

.department {
  font-size: 14px;
  color: #777;
}

.account-section {
  background: #fff;
  border-radius: 10px;
  padding: 20px 24px;
  border: 1px solid #e3e3e3;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 18px;
}

.account-section h3 {
  font-size: 20px;
  color: #222;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-group label {
  font-weight: 500;
  color: #555;
}

.form-group input {
  padding: 10px 12px;
  border: 1px solid #ccc;
  border-radius: 6px;
  font-size: 15px;
  transition: 0.2s border-color;
}

.form-group input:focus {
  border-color: #007bff;
  outline: none;
}

.preferences {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.checkbox {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  color: #333;
}

/* Action Buttons */
.actions.spaced {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 10px;
}

.btn {
  padding: 10px 20px;
  border-radius: 6px;
  border: 1px solid #ccc;
  background: #fff;
  cursor: pointer;
  transition: 0.2s all;
  font-weight: 500;
}

.btn:hover {
  background: #f0f0f0;
}

.btn.primary {
  background: #007bff;
  color: #fff;
  border-color: #007bff;
}

.btn.primary:hover {
  background: #0056d2;
}

.btn.danger {
  background: #dc3545;
  color: #fff;
  border-color: #dc3545;
}

.btn.danger:hover {
  background: #b02a37;
}

/* Responsive */
@media (max-width: 600px) {
  .profile-header {
    flex-direction: column;
    align-items: flex-start;
  }
  .avatar {
    width: 70px;
    height: 70px;
    font-size: 22px;
  }
  .account-page {
    padding: 20px 16px;
  }
  .actions.spaced {
    flex-direction: column;
    gap: 12px;
  }
}
</style>
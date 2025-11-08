<template>
  <div class="dashboard">

    <main class="dashboard-content">
      <h1>Add a new Employee</h1>
      <div class="employee-list">
        <div class="employee-item">
          <div class="form-group">
            <label for="employeeName" class="field-label">Employee Name</label>
            <input
              class="text-input"
              type="text"
              name="employeeName"
              id="employeeName"
              placeholder="Enter full name"
              v-model="employeeName"
            />
          </div>

          <div class="form-group">
            <label for="employeeType" class="field-label">Select Employee Type</label>
            <select class="status-dropdown" id="employeeType" v-model="employeeType">
              <option value="">Choose a role</option>
              <option value="HR">HR</option>
              <option value="Product Manager">Product Manager</option>
              <option value="Employee">Employee</option>
            </select>
          </div>

          <div class="form-actions">
            <button class="btn" @click="AddEmployee">Add Employee</button>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script>
export default {
  name: 'AdminAddEmployee',
  data() {
    return {
      employeeName: '',
      employeeType: ''
    };
  },
  methods: {
    AddEmployee() {
      // Logic to add employee
      console.log(`Employee Name: ${this.employeeName}, Employee Type: ${this.employeeType}`);
      // Reset fields
      this.employeeName = '';
      this.employeeType = '';
    }
  }
};
</script>

<style scoped>
/* All styles are identical to ChatbotConfig.vue */
.dashboard {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  background-color: #f4f7f6;
  height: 100vh;
  color: #333;
}
a { text-decoration: none; color: #555; font-size: 14px; }
a:hover { color: #000; }
.router-link-exact-active { color: #007bff; font-weight: bold; }
.dashboard-header { display: flex; justify-content: space-between; align-items: center; padding: 15px 30px; background-color: #ffffff; border-bottom: 1px solid #ddd; }
.nav-links a { margin-right: 25px; }
.account-link a { font-weight: bold; }
.dashboard-content { padding: 25px 30px; }
.dashboard-content h1 { margin: 0; font-size: 28px; font-weight: 600; margin-bottom: 20px; }
.content-placeholder { background-color: #fff; border: 1px solid #ddd; border-radius: 8px; padding: 20px; min-height: 200px; }

/* Add Employee card layout */
.employee-list {
  max-width: 640px;
  margin: 16px auto 0;
}

.employee-item {
  background: #ffffff;
  border: 1px solid #e5e7eb; 
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 10px 24px rgba(0, 0, 0, 0.05);
}

.form-group { margin-bottom: 16px; }
.field-label {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: #374151; 
  margin-bottom: 8px;
}

.text-input,
.status-dropdown {
  width: 100%;
  padding: 10px 12px;
  font-size: 14px;
  color: #111827; 
  background: #fff;
  border: 1px solid #d1d5db; 
  border-radius: 8px;
  outline: none;
  transition: border-color 0.15s ease, box-shadow 0.15s ease;
}

.text-input::placeholder { color: #9ca3af; }

.text-input:focus,
.status-dropdown:focus {
  border-color: #007bff;
  box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.15);
}

.form-actions { margin-top: 8px; }

.btn {
  padding: 10px 14px;
  border: none;
  border-radius: 8px;
  background-color: #007bff;
  color: #ffffff;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  box-shadow: 0 6px 14px rgba(0, 123, 255, 0.25);
  transition: background-color 0.15s ease, transform 0.05s ease, box-shadow 0.15s ease;
}

.btn:hover { background-color: #0069d9; box-shadow: 0 8px 18px rgba(0, 123, 255, 0.3); }
.btn:active { transform: translateY(0.5px); }
.btn:disabled { background-color: #a5b4fc; cursor: not-allowed; box-shadow: none; }
</style>
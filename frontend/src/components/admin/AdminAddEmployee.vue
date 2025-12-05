<template>
  <div class="row justify-content-center">
    <div class="col-12 col-md-8 col-lg-6">
      <div class="card border-0 shadow-sm rounded-4">
        <div class="card-body p-4 p-md-5">
          <h1 class="h3 fw-bold mb-4 text-center">Add a New Employee</h1>

          <div class="mb-4">
            <label for="employeeName" class="form-label fw-medium">Employee Name</label>
            <input type="text" class="form-control bg-light border-0" id="employeeName" placeholder="Enter full name"
              v-model="employeeName" />
          </div>

          <div class="mb-5">
            <label for="employeeType" class="form-label fw-medium">Select Employee Type</label>
            <select class="form-select bg-light border-0" id="employeeType" v-model="employeeType">
              <option value="">Choose a role</option>
              <option value="HR">HR</option>
              <option value="Product Manager">Product Manager</option>
              <option value="Employee">Employee</option>
            </select>
          </div>

          <div class="d-grid">
            <button class="btn btn-primary py-2 fw-semibold shadow-sm" @click="AddEmployee">
              Add Employee
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { make_postrequest } from '@/store/appState';

export default {
  name: 'AdminAddEmployee',
  data() {
    return {
      employeeName: '',
      employeeType: ''
    };
  },
  methods: {
    async AddEmployee() {
      if (!this.employeeName || !this.employeeType) {
        alert('Please fill in all fields.');
        return;
      }
      try {
        const data = await make_postrequest('/api/admin/employees', {
          name: this.employeeName,
          role: this.employeeType
        });
        alert(`Employee added successfully: ${data.name}\n\nDetails:\nID: ${data.id}\nRole: ${data.role}\nEmail: ${data.email}\nPassword: ${data.temporary_password}`);
        this.employeeName = '';
        this.employeeType = '';
      } catch (error) {
        console.error('Failed to add employee', error);
      }
    }
  },
  mounted() {
    const user = JSON.parse(localStorage.getItem('user'));
    if (!localStorage.getItem('token') || user.role !== 'root') {
      alert('Please login to access the admin dashboard.');
      this.$router.push('/login');
      return;
    }
  },
};
</script>
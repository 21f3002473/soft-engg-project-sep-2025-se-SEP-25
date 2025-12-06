<template>
  <nav class="navbar navbar-expand-lg sticky-top py-3 shadow-sm custom-navbar">
    <div class="container-fluid" style="max-width: 1250px;">

      <div class="d-flex align-items-center flex-wrap gap-3 gap-lg-4 w-100 justify-content-between">

        <div class="d-flex align-items-center gap-3 gap-lg-4 flex-wrap">
          <div class="navbar-brand fw-bold text-primary fs-4 me-0" style="letter-spacing: 0.5px;">Sync'em</div>

          <ul class="nav nav-pills d-flex gap-2">
            <li class="nav-item">
              <router-link :to="{ name: 'EmployeeDashboard' }" class="nav-link" active-class="active">
                <i class="bi bi-speedometer2 me-2"></i>Dashboard
              </router-link>
            </li>
            <li class="nav-item">
              <router-link :to="{ name: 'EmployeeLearning' }" class="nav-link" active-class="active">
                <i class="bi bi-mortarboard me-2"></i>Learning
              </router-link>
            </li>
            <li class="nav-item">
              <router-link :to="{ name: 'EmployeeRequests' }" class="nav-link" active-class="active">
                <i class="bi bi-file-earmark-plus me-2"></i>Requests
              </router-link>
            </li>
            <li class="nav-item">
              <router-link :to="{ name: 'EmployeeHRFAQs' }" class="nav-link" active-class="active">
                <i class="bi bi-question-circle me-2"></i>HR FAQs
              </router-link>
            </li>
            <li class="nav-item">
              <router-link :to="{ name: 'EmployeeWriting' }" class="nav-link" active-class="active">
                <i class="bi bi-pencil-square me-2"></i>Writing
              </router-link>
            </li>
          </ul>
        </div>

        <div class="d-flex align-items-center gap-3">
          <router-link :to="{ name: 'EmployeeAccount' }"
            class="btn d-flex align-items-center gap-2 fw-semibold account-btn" active-class="active">
            <i class="bi bi-person-circle fs-5"></i>
            <span>Account</span>
          </router-link>
          <button class="btn d-flex align-items-center gap-2 fw-semibold account-btn" @click="logout">
            <i class="bi bi-box-arrow-right fs-5"></i>
            <span>Logout</span>
          </button>
        </div>

      </div>
    </div>
  </nav>
</template>

<script>
import Swal from 'sweetalert2';

export default {
  name: 'EmployeeNavBar',
  methods: {
    async logout() {
      const result = await Swal.fire({
        title: 'Logout?',
        text: "Are you sure you want to logout?",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#3085d6',
        cancelButtonColor: '#d33',
        confirmButtonText: 'Yes, logout!'
      });

      if (result.isConfirmed) {
        this.$store.dispatch('logout');
        this.$router.push({ name: 'Login' });
      }
    }
  }
};
</script>

<style scoped>
.custom-navbar {
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
  z-index: 100;
}

.nav-link {
  color: #334155;
  font-weight: 500;
  font-size: 17px;
  padding: 8px 16px;
  border-radius: 8px;
  transition: all 0.25s ease;
}

.nav-link:hover {
  color: #1d4ed8;
  background: rgba(37, 99, 235, 0.1);
  transform: translateY(-2px);
}

.nav-link.active {
  background: linear-gradient(135deg, #2563eb, #1d4ed8) !important;
  color: white !important;
  font-weight: 600;
  box-shadow: 0 4px 10px rgba(37, 99, 235, 0.3);
}

.search-input {
  width: 250px;
  background: rgba(241, 245, 255, 0.9);
  border: none;
  box-shadow: inset 0 0 0 1px rgba(37, 99, 235, 0.2);
  font-size: 15px;
  transition: all 0.3s ease;
}

.search-input:focus {
  width: 300px;
  background: #fff;
  box-shadow: 0 0 0 2px #3b82f6;
}

.account-btn {
  font-size: 16px;
  color: #1e3a8a;
  border: none;
  padding: 8px 16px;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.account-btn:hover {
  background: rgba(37, 99, 235, 0.1);
  color: #1e3a8a;
}

.account-btn.active {
  background: linear-gradient(135deg, #2563eb, #1d4ed8);
  color: white;
  box-shadow: 0 4px 10px rgba(37, 99, 235, 0.3);
}

@media (max-width: 576px) {
  .search-input {
    width: 100%;
  }

  .search-input:focus {
    width: 100%;
  }
}
</style>
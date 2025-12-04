<template>
  <nav class="navbar navbar-expand-lg sticky-top py-3 shadow-sm custom-navbar">
    <div class="container-fluid" style="max-width: 1250px;">
      
      <div class="d-flex align-items-center flex-wrap gap-3 gap-lg-4 w-100 justify-content-between">
        
        <div class="d-flex align-items-center gap-3 gap-lg-4 flex-wrap">
          <div class="navbar-brand fw-bold text-primary fs-4 me-0" style="letter-spacing: 0.5px;">Sync'em</div>
          
          <ul class="nav nav-pills d-flex gap-2">
            <li class="nav-item">
              <router-link :to="{ name: 'EmployeeDashboard' }" class="nav-link" active-class="active">Dashboard</router-link>
            </li>
            <li class="nav-item">
              <router-link :to="{ name: 'EmployeeLearning' }" class="nav-link" active-class="active">Learning</router-link>
            </li>
            <li class="nav-item">
              <router-link :to="{ name: 'EmployeeRequests' }" class="nav-link" active-class="active">Requests</router-link>
            </li>
            <li class="nav-item">
              <router-link :to="{ name: 'EmployeeHRFAQs' }" class="nav-link" active-class="active">HR FAQs</router-link>
            </li>
            <li class="nav-item">
              <router-link :to="{ name: 'EmployeeWriting' }" class="nav-link" active-class="active">Writing</router-link>
            </li>
          </ul>
        </div>

        <div class="d-flex align-items-center gap-3">
          <div class="position-relative d-none d-sm-block">
            <i class="fas fa-search position-absolute text-muted" style="top: 50%; left: 12px; transform: translateY(-50%); font-size: 18px;"></i>
            <input type="search" placeholder="Search..." class="form-control rounded-pill ps-5 search-input" />
          </div>
          
          <router-link :to="{ name: 'EmployeeAccount' }" class="btn d-flex align-items-center gap-2 fw-semibold account-btn" active-class="active">
            <i class="fas fa-user-circle fs-5"></i>
            <span>Account</span>
          </router-link>
        </div>

      </div>
    </div>
  </nav>
</template>

<script>
export default {
  name: 'EmployeeNavBar'
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
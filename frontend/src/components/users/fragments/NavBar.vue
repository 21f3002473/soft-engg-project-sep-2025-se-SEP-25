<template>
  <header class="top-nav">
    <nav class="nav-inner">
      <div class="nav-left">
        <div class="brand">
          <p class="brand-name">Sync'em</p>
        </div>

        <ul class="nav-links">
          <li><router-link to="/user/dashboard" active-class="active">Dashboard</router-link></li>
          <li><router-link to="/user/learning" active-class="active">Learning</router-link></li>
          <li><router-link to="/user/requests" active-class="active">Requests</router-link></li>
          <li><router-link to="/user/hr-faqs" active-class="active">HR FAQs</router-link></li>
          <li><router-link to="/user/writing-section" active-class="active">Writing</router-link></li>
        </ul>
      </div>

      <!-- Right Section -->
      <div class="nav-right">
        <div class="search-container mx-3">
          <i class="fas fa-search"></i>
          <input type="search" placeholder="Search..." class="nav-search" />
        </div>
        <router-link to="/user/account" active-class="active" class="account">
          <i class="fas fa-user-circle"></i>
          <span>Account</span>
        </router-link>
      </div>
    </nav>
  </header>
</template>

<script>
export default {
  name: 'NavBar'
};
</script>

<style scoped>
/* Navbar Base */
.top-nav {
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
}

.nav-inner {
  max-width: 1250px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 30px; /* slightly increased horizontal padding */
}

/* Left Section */
.nav-left {
  display: flex;
  align-items: center;
  gap: 32px;
  flex-shrink: 1;
  min-width: 0;
}

/* Brand */
.brand {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 10px;
}

.brand-name {
  font-size: 23px;
  font-weight: 700;
  color: #2563eb;
  white-space: nowrap;
  letter-spacing: 0.5px;
  transform: translateY(1px); /* tiny visual alignment tweak */
}

/* Navigation Links */
.nav-links {
  list-style: none;
  display: flex;
  align-items: center;
  gap: 22px;
  margin: 0;
  padding: 0;
}

.nav-links a {
  text-decoration: none;
  color: #334155;
  font-weight: 500;
  font-size: 15px;
  padding: 8px 12px;
  border-radius: 8px;
  transition: all 0.25s ease;
}

.nav-links a:hover {
  color: #1d4ed8;
  background: rgba(37, 99, 235, 0.1);
  transform: translateY(-2px);
}

.nav-links a.active {
  background: linear-gradient(135deg, #2563eb, #1d4ed8);
  color: white;
  font-weight: 600;
  box-shadow: 0 4px 10px rgba(37, 99, 235, 0.3);
}

/* Right Section */
.nav-right {
  display: flex;
  align-items: center;
  gap: 18px;
  flex-shrink: 0;
}

/* Search */
.search-container {
  position: relative;
}

.search-container i {
  position: absolute;
  top: 50%;
  left: 12px;
  transform: translateY(-50%);
  color: #64748b;
  font-size: 14px;
}

.nav-search {
  border: none;
  background: rgba(241, 245, 255, 0.9);
  border-radius: 20px;
  padding: 8px 14px 8px 34px;
  width: 250px;
  transition: all 0.3s ease;
  font-size: 14px;
  color: #1e293b;
  box-shadow: inset 0 0 0 1px rgba(37, 99, 235, 0.2);
}

.nav-search:focus {
  outline: none;
  width: 300px;
  box-shadow: 0 0 0 2px #3b82f6;
}

/* Account */
.account {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #1e3a8a;
  text-decoration: none;
  font-weight: 600;
  font-size: 15px;
  padding: 8px 12px;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.account:hover {
  background: rgba(37, 99, 235, 0.1);
}

.account.active {
  background: linear-gradient(135deg, #2563eb, #1d4ed8);
  color: white;
  box-shadow: 0 4px 10px rgba(37, 99, 235, 0.3);
}

/* Responsiveness */
@media (max-width: 850px) {
  .nav-inner {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }

  .nav-left {
    flex-wrap: wrap;
    gap: 12px;
  }

  .nav-links {
    flex-wrap: wrap;
    gap: 12px;
  }

  .nav-search {
    width: 160px;
  }
}
</style>
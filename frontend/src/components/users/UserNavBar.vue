<template>
  <header class="top-nav">
    <nav class="nav-inner">
      <ul class="nav-left">
        <li><router-link to="/user/dashboard" active-class="active">Dashboard</router-link></li>
        <li><router-link to="/user/learning" active-class="active">Learning</router-link></li>
        <li><router-link to="/user/requests" active-class="active">Requests</router-link></li>
        <li><router-link to="/user/hr-faqs" active-class="active">HR FAQs</router-link></li>
        <li><router-link to="/user/writing-section" active-class="active">Writing Section</router-link></li>
      </ul>
      <div class="nav-right">
        <input class="nav-search" type="search" placeholder="Search" />
        <router-link to="/user/account" active-class="active" class="account">Account</router-link>
      </div>
    </nav>
  </header>
</template>

<script>
export default {
  name: 'UserNavBar'
};
</script>

<style scoped>
.top-nav {
  background: #fff;
  border-bottom: 1px solid #e6e6e6;
  position: sticky;
  top: 0;
  z-index: 100;
}
.nav-inner {
  max-width: 1100px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
}
.nav-left {
  list-style: none;
  display: flex;
  align-items: center;
  gap: 18px;
  margin: 0;
  padding: 0;
  font-family: "Segoe UI", Roboto, "Helvetica Neue", Arial;
  color: #333;
}
.brand {
  font-weight: 600;
  margin-right: 8px;
}
.nav-left a {
  color: #333;
  text-decoration: none;
  padding: 6px 8px;
  border-radius: 6px;
}
.nav-left a:hover {
  background: #f3f3f3;
}
.nav-left a.active {
  background: #f3f3f3;
  font-weight: 600;
}
.nav-right {
  display: flex;
  align-items: center;
  gap: 12px;
}
.nav-search {
  border: 1px solid #ddd;
  padding: 8px 12px;
  border-radius: 20px;
  width: 220px;
}
.account {
  color: #333;
  text-decoration: none;
  padding: 6px 10px;
  border-radius: 6px;
}
.account.active {
  background: #f3f3f3;
  font-weight: 600;
}
</style>

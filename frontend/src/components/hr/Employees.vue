<template>
  <div class="employees-root">

    

    <!-- Main Section -->
    <section class="employees-section">
      <div class="employees-container">
        <!-- Left: Performance Review Table -->
        <div class="employees-left">
          <div class="header-row">
            <h1 class="employees-title">Performance Reviews</h1>
            <input
              type="text"
              class="search-input"
              placeholder="Search Employee..."
            />
          </div>

          <table class="employees-table">
            <thead>
              <tr>
                <th>Employee</th>
                <th>Status</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(emp, index) in employees" :key="index">
                <td>{{ emp.name }}</td>
                <td>{{ emp.status }}</td>
                <td>
                  <button
                    :class="['review-btn', emp.status === 'Done' ? 'done' : '']"
                  >
                    {{ emp.status === 'Upcoming' ? 'Auto Review' : 'Re-Auto Review' }}
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Right: Review Gen Panel -->
        <div class="employees-right">
          <h2 class="reviewgen-title">Review Gen</h2>
          <p>
            Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec sit amet lacus a justo
            viverra tristique. Morbi blandit accumsan eros, nec elementum eros posuere eget. Duis
            varius commodo elit, eget gravida ligula pretium ut.
          </p>
        </div>
      </div>
    </section>

    <!-- Footer -->
    <footer class="footer">
      <p>© 2025 Sync'em. All rights reserved.</p>
    </footer>
  </div>
</template>

<script>
export default {
  name: 'HrEmployees',
  data() {
    return {
      employees: [
        { name: 'EMP1', status: 'Upcoming' },
        { name: 'EMP2', status: 'Upcoming' },
        { name: 'EMP3', status: 'Upcoming' },
        { name: 'EMP4', status: 'Done' },
        { name: 'EMP5', status: 'Done' },
        { name: 'EMP6', status: 'Done' }
      ]
    }
  }
}
</script>

<style scoped>
.employees-root {
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue',
    Arial;
  color: #fff;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  overflow-x: hidden;
  background: url('../../assets/images/landing/landingPageBackgroundImage.png') no-repeat center
    center/cover;
  background-color: rgba(10, 20, 70, 0.85);
  background-blend-mode: overlay;
}

/* Navbar */
.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(90, 160, 255, 0.08);
  backdrop-filter: blur(4px);
  padding: 20px 60px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.15);
}
.brand {
  font-style: italic;
  font-weight: 700;
  color: #ffffff;
  font-size: 22px;
}
.nav-right {
  display: flex;
  align-items: center;
}
.nav-link {
  color: white;
  text-decoration: none;
  margin-left: 25px;
  font-size: 16px;
  transition: color 0.3s;
}
.nav-link:hover,
.nav-link.active {
  color: #dce3ff;
}

/* Section Layout */
.employees-section {
  flex-grow: 1;
  display: flex;
  justify-content: center;
  align-items: flex-start;
  padding: 80px 20px;
  color: white;
}

.employees-container {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 40px;
  width: 90%;
  max-width: 1100px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 40px 50px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

/* Left Column */
.employees-left {
  display: flex;
  flex-direction: column;
}
.header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.employees-title {
  font-size: 28px;
  color: #e2e8ff;
  font-weight: 700;
}

/* Search Bar beside title */
.search-input {
  background: rgba(255, 255, 255, 0.95);
  border: none;
  border-radius: 8px;
  padding: 8px 14px;
  font-size: 15px;
  color: #1e3a8a;
  outline: none;
  width: 200px;
}

/* Table */
.employees-table {
  width: 100%;
  border-collapse: collapse;
}
.employees-table th,
.employees-table td {
  padding: 12px 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  text-align: left;
}
.review-btn {
  background: linear-gradient(90deg, #6366f1, #3b82f6);
  border: none;
  color: white;
  border-radius: 8px;
  padding: 8px 16px;
  cursor: pointer;
  font-weight: 600;
  transition: transform 0.2s;
}
.review-btn:hover {
  transform: translateY(-2px);
  background: linear-gradient(90deg, #818cf8, #60a5fa);
}
.review-btn.done {
  background: linear-gradient(90deg, #10b981, #059669);
}

/* Right Column (Review Gen) */
.employees-right {
  background: rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  padding: 25px;
  border: 1px solid rgba(255, 255, 255, 0.2);
}
.reviewgen-title {
  font-size: 22px;
  color: #f1f5f9;
  margin-bottom: 12px;
}

/* Footer */
.footer {
  text-align: center;
  padding: 16px 0;
  color: #e5e7eb;
  background: rgba(0, 0, 0, 0.3);
  font-size: 14px;
  border-top: 1px solid rgba(255, 255, 255, 0.15);
}
</style>

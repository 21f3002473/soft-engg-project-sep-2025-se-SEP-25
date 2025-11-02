<template>
  <div class="container-fluid py-4">
    <div class="container">
      <div class="row g-4">
        <!-- Left: PDF viewer -->
        <div class="col-12 col-md-6">
          <div class="card h-100">
            <div class="card-body p-0">
              <div class="ratio ratio-4x3">
                <iframe
                  src="https://triagelogic.com/wp-content/uploads/2018/06/Company-Policy-and-Procedure-June-1.18-V6.0.pdf"
                  frameborder="0"
                  class="w-100 h-100"
                ></iframe>
              </div>
            </div>
            <div class="card-footer text-muted small">Company Policies</div>
          </div>
        </div>

        <!-- Right: Ask HR / Chatbot box -->
        <div class="col-12 col-md-6">
          <div class="card h-100">
            <div class="card-body d-flex flex-column">
              <h5 class="card-title">HR Policies — Ask Here</h5>

              <textarea
                v-model="query"
                placeholder="Type your question about HR policies..."
                class="form-control mb-3 flex-grow-1"
                rows="6"
              ></textarea>

              <div class="d-flex gap-2">
                <button class="btn btn-primary" @click="submitQuery">Ask</button>
                <button class="btn btn-outline-secondary" type="button" @click="query = ''">Clear</button>
              </div>

              <div v-if="response" class="alert alert-secondary mt-3" role="alert">
                <strong>Response:</strong>
                <div>{{ response }}</div>
              </div>
            </div>

            <div class="card-footer text-muted small">Need more help? Contact HR.</div>
          </div>
        </div>
      </div>

      <footer class="mt-4 text-center text-muted">© 2025 Sync'em. All rights reserved.</footer>
    </div>
  </div>
</template>

<script>
export default {
  name: "HrPoliciesPage",
  data() {
    return {
      query: "",
      response: "",
    };
  },
  methods: {
    submitQuery() {
      if (this.query.trim() === "") {
        this.response = "Please type a question first.";
        return;
      }
      // Simulated chatbot reply
      this.response = `This is an automated response to: "${this.query}"`;
      this.query = "";
    },
  },
};
</script>

<!-- <style scoped>
.hrpolicies-root {
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial;
  color: #fff;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  /* background: url('../../assets/images/landing/landingPageBackgroundImage.png') no-repeat center center/cover; */
  /* background-color: rgba(20, 40, 108, 0.85);
  background-blend-mode: overlay; */
}

/* Navbar */
.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(90, 160, 255, 0.1);
  backdrop-filter: blur(4px);
  padding: 20px 40px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  position: sticky;
  top: 0;
  z-index: 10;

  /* ensure navbar does not wrap its children */
  flex-wrap: nowrap;
}

/* left brand (keeps it compact) */
.brand {
  font-style: italic;
  font-weight: 700;
  color: #ffffff;
  font-size: 24px;
  line-height: 1;
  white-space: nowrap;
}

/* right group: always horizontal, with gap between links */
.nav-right {
  display: flex;
  align-items: center;
  gap: 20px;        /* spacing between links */
  flex-wrap: nowrap; /* prevent wrapping into multiple rows */
  justify-content: flex-end;
}

/* ensure each link stays on one line and is inline-flex for vertical centering */
.nav-link {
  display: inline-flex;
  align-items: center;
  white-space: nowrap; /* prevent internal wrapping of long labels */
  color: white;
  text-decoration: none;
  font-size: 18px;
  margin-left: 0;      /* gap handled by .nav-right gap */
  padding: 6px 8px;
  transition: color 0.3s;
}

/* hover / active styles unchanged */
.nav-link:hover,
.nav-link.active {
  color: #dce3ff;
}
.brand {
  font-style: italic;
  font-weight: 700;
  color: #ffffff;
  font-size: 24px;
}
.nav-link {
  color: white;
  text-decoration: none;
  font-size: 18px;
  margin-left: 25px;
  transition: color 0.3s;
}
.nav-link:hover,
.nav-link.active {
  color: #dce3ff;
}

/* Main section */
.hrpolicies-section {
  flex-grow: 1;
  display: flex;
  justify-content: center;
  padding: 60px 20px;
}

/* 🔹 Changed to 50%-50% layout */
.hrpolicies-container {
  display: grid;
  grid-template-columns: 1fr 1fr; /* Equal split */
  gap: 40px;
  width: 90%;
  max-width: 1200px;
  background: rgba(255, 255, 255, 0.15);
  border-radius: 16px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  padding: 40px;
}

/* PDF Viewer */
.pdf-viewer {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.25);
  display: flex;
  align-items: center;
  justify-content: center;
}
.pdf-frame {
  width: 100%;
  height: 600px;
  border: none;
}

/* Ask box */
.ask-box {
  display: flex;
  flex-direction: column;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 20px;
  border: 1px solid rgba(255, 255, 255, 0.25);
}
.ask-title {
  font-size: 22px;
  color: #c7d2fe;
  font-weight: 600;
  margin-bottom: 15px;
  text-align: center;
}
.ask-input {
  background: rgba(255, 255, 255, 0.9);
  color: #1e3a8a;
  border: none;
  border-radius: 8px;
  padding: 12px;
  font-size: 16px;
  min-height: 180px;
  resize: vertical;
  outline: none;
}
.ask-button {
  background: linear-gradient(90deg, #6366f1, #3b82f6);
  border: none;
  color: white;
  border-radius: 8px;
  padding: 10px;
  font-size: 16px;
  margin-top: 15px;
  cursor: pointer;
  font-weight: 600;
  transition: transform 0.2s;
}
.ask-button:hover {
  transform: translateY(-2px);
  background: linear-gradient(90deg, #818cf8, #60a5fa);
}
.response-box {
  background: rgba(255, 255, 255, 0.15);
  border-radius: 8px;
  padding: 12px;
  margin-top: 20px;
  color: #e0e7ff;
  font-size: 15px;
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

/* Responsive */
@media (max-width: 900px) {
  .hrpolicies-container {
    grid-template-columns: 1fr;
  }
  .pdf-frame {
    height: 400px;
  }
}
</style> -->

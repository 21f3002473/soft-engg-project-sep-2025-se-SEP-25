<template>
  <div class="chatbot-root">
    <section class="chat-section py-5">
      <div class="container">
        <div class="row justify-content-center">
          <div class="col-12 col-md-8 col-lg-6">
            <div class="card shadow-sm">
              <div class="card-body">
                <h1 class="card-title h4 mb-3">Chatbot (ask here)</h1>
                <div class="mb-3">
                  <textarea
                    class="form-control"
                    placeholder="Type your question for the HR Chatbot..."
                    rows="8"
                  ></textarea>
                </div>
                <div class="d-flex justify-content-end">
                  <button class="btn btn-primary">Submit</button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- <footer class="footer bg-light py-3">
      <div class="container text-center">
        <p class="mb-0">© 2025 Sync'em. All rights reserved.</p>
      </div>
    </footer> -->
  </div>
</template>

<script>
export default {
  name: 'HRChatbot'
}
</script>

<!-- <style scoped>
.chatbot-root {
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue',
    Arial;
  color: #0b1220;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  overflow-x: hidden;
  /* background: url('../../assets/images/landing/landingPageBackgroundImage.png') no-repeat center
    center/cover; */
  /* background-color: rgba(20, 40, 108, 0.85);
  background-blend-mode: overlay; */
}

/* Navbar - fully transparent light blue */
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
}

.nav-left {
  font-size: 24px;
  color: white;
  font-weight: 600;
}

.brand {
  font-style: italic;
  font-weight: 700;
  letter-spacing: 0.5px;
  color: #ffffff;
}

.nav-right {
  display: flex;
  align-items: center;
}

.nav-link {
  color: white;
  text-decoration: none;
  font-size: 18px;
  margin-left: 25px;
  font-weight: 500;
  transition: color 0.3s ease;
}

.nav-link:hover {
  color: #dce3ff;
}

/* Chat Section */
.chat-section {
  display: flex;
  justify-content: center;
  align-items: center;
  flex-grow: 1;
  padding: 60px 20px;
  color: white;
}

.chat-box {
  background: rgba(255, 255, 255, 0.15);
  border-radius: 16px;
  padding: 40px;
  width: 90%;
  max-width: 700px;
  text-align: center;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.chat-title {
  font-size: 32px;
  color: #e2e8ff;
  margin-bottom: 20px;
  font-weight: 700;
}

.chat-input {
  width: 100%;
  border-radius: 10px;
  padding: 16px;
  font-size: 16px;
  color: #1e3a8a;
  border: none;
  outline: none;
  resize: none;
  background: rgba(255, 255, 255, 0.9);
  margin-bottom: 20px;
  font-family: inherit;
}

.chat-submit {
  background: linear-gradient(90deg, #6366f1, #3b82f6);
  color: white;
  border: none;
  border-radius: 8px;
  padding: 12px 24px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition:
    transform 0.3s ease,
    background 0.3s ease;
}

.chat-submit:hover {
  background: linear-gradient(90deg, #818cf8, #60a5fa);
  transform: translateY(-2px);
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
</style> -->

<template>
  <div class="chatbot-content">
    <div class="row justify-content-center">
      <div class="col-12 col-md-8 col-lg-6">
        <div class="card border-0 shadow-sm rounded-3">
          <div class="card-body p-4">
            <h1 class="card-title h4 mb-3 fw-bold text-primary">HR Assistant</h1>
            <div class="mb-3">
              <textarea class="form-control" placeholder="Type your question for the HR Chatbot..." rows="8"></textarea>
            </div>
            <div class="d-flex justify-content-end">
              <button class="btn btn-primary d-flex align-items-center gap-2">
                <i class="bi bi-send"></i> Ask
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'HRChatbot'
}
</script>
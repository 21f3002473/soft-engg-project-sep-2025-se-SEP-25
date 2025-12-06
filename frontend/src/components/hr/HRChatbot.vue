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
  </div>
</template>

<script>
export default {
  name: 'HRChatbot'
}
</script>
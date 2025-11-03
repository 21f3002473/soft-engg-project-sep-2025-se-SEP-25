<template>
  <div class="container-fluid py-4">
    <div class="row g-4">
      
      <div class="col-lg-3 col-md-4">
        <div class="card shadow-sm">
          <div class="card-body text-center">
            <img
              :src="`https://dummyjson.com/icon/${clientId}/150`"
              alt="Client Image"
              class="img-fluid rounded-circle mb-3 border border-3 border-primary"
              style="width: 150px; height: 150px; object-fit: cover;"
            />
            <h4 class="card-title mb-2">Client ID: {{ clientId }}</h4>
            <p class="card-text text-muted">Details about Client with ID: {{ clientId }}</p>
          </div>
        </div>
      </div>

      
      <div class="col-lg-9 col-md-8">
        <div class="card shadow-sm h-100">
          <div class="card-header bg-primary text-white">
            <h3 class="h5 mb-0">Client Updates</h3>
          </div>
          <div class="card-body">
            <div class="d-flex flex-column flex-md-row gap-3 align-items-start">
              
              <div class="flex-md-shrink-0" style="min-width: 280px;">
                <div class="alert alert-light border mb-0">
                  <p class="text-muted mb-3">Updates and details for client {{ clientId }}</p>
                  <ul class="list-group list-group-flush">
                    <li class="list-group-item">
                      <strong class="text-primary">Update 1:</strong>
                      <span class="ms-2">Description of update 1.</span>
                    </li>
                    <li class="list-group-item">
                      <strong class="text-primary">Update 2:</strong>
                      <span class="ms-2">Description of update 2.</span>
                    </li>
                    <li class="list-group-item">
                      <strong class="text-primary">Update 3:</strong>
                      <span class="ms-2">Description of update 3.</span>
                    </li>
                  </ul>
                </div>
              </div>

              <div class="flex-fill border rounded p-3 bg-light" style="min-height: 400px;">
                <div class="d-flex align-items-center mb-3 pb-2 border-bottom">
                  <i class="bi bi-chat-dots-fill text-primary me-2 fs-5"></i>
                  <h5 class="mb-0">AI Assistant</h5>
                </div>
                <Chatbot />
              </div>

            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

</template>
<script>

import Chatbot from './fragments/Chatbot.vue';

export default{
    name: "UpdateClient",
    props:{
        clientId:{type:String}
    },
    components:{
        Chatbot
    }
}

</script>
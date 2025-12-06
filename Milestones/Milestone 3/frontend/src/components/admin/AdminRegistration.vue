<template>
  <div class="registration-view">
	<!-- Registration view content -->
     <h1>Admin Registration</h1>
     <form @submit.prevent="registerAdmin">
       <div>
         <label for="name">Name:</label>
         <input type="text" id="name" v-model="name" required />
       </div>
       <div>
         <label for="email">Email:</label>
         <input type="email" id="email" v-model="email" required />
       </div>
       <div>
         <label for="password">Password:</label>
         <input type="password" id="password" v-model="password" required />
       </div>
       <button type="submit">Register</button>
     </form>
  </div>
</template>

<script>
export default {
  name: 'AdminRegistration',
  data() {
    return {
      name: '',
      email: '',
      password: ''
    };
  },
  methods: {
    registerAdmin() {
      console.log('Admin registered:', this.name, this.email, this.password);
    }
  }
};
</script>

<style scoped>
.registration-view {
  max-width: 400px;
  margin: 0 auto;
  padding: 20px;
  border: 1px solid #ccc;
  border-radius: 5px;
}
</style>

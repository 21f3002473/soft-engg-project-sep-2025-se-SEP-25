<template>
    <div class="container py-5">
        <h1 class="text-center mb-4">Login Page</h1>
        <div class="row justify-content-center">
            <div class="col-md-6 col-lg-4">
                <div class="card shadow-sm">
                    <div class="card-body">
                        <h3 class="card-title mb-4 text-center">Login</h3>
                        <form class="needs-validation" novalidate @submit.prevent="submitLogin">
                            <div class="mb-3">
                                <label for="email" class="form-label">email</label>
                                <input type="email" class="form-control" id="email" v-model="email" name="email" required />
                                <div class="invalid-feedback">Please enter a email.</div>
                            </div>

                            <div class="mb-3">
                                <label for="password" class="form-label">Password</label>
                                <input type="password" v-model="password" class="form-control" id="password" name="password" required />
                                <div class="invalid-feedback">Please enter a password.</div>
                            </div>

                            <div class="d-grid">
                                <button type="submit" class="btn btn-primary">Login</button>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>

import axios from 'axios';
export default {
    name: 'LoginPageView',
    data() {
        return {
            email: '',
            password: ''
        };
    },
    methods: {
        async submitLogin() {

            // Handle login logic here
            console.log('Email:', this.email);
            console.log('Password:', this.password);


            try {
        const response = await axios.post("http://localhost:8000/user/login", {
          email: this.email,
          password: this.password,
        });

        console.log("Login successful:", response.data);
        // const { access_token, user } = response.data;

        // if (access_token && user) {
        //   setToken(access_token);
        //   setUser(user);
        //   setIsAuthenticated(true);

        //   if (user.role === "admin") {
        //     this.$router.push({ name: "home" });
        //   } else if (user.role === "user") {
        //     this.$router.push({ name: "user_dashboard" });
        //   } else {
        //     throw new Error("Unknown user role");
        //   }
        // } else {
        //   throw new Error("Invalid response format - missing token or user");
        // }
      } catch (error) {
        console.error("Login failed:", error);

        // setToken("");
        // setUser({ id: null, username: "", role: "" });
        // setIsAuthenticated(false);

        this.error =
          error.response?.data?.message ||
          "Login failed. Please check your credentials.";
      } finally {
        this.loading = false;
      }

    },
},
    mounted() {
        // Code to run when the component is mounted
    }
};
</script>
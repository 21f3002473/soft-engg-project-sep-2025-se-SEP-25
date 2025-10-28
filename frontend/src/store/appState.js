export async function submitLogin(url, params = {}) {
    const res = await fetch(location.origin + "/user/login", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            email: "this.email",
            password: "this.password",
        }),
    });
    if (res.ok) {
        const data = await res.json();
        localStorage.setItem("auth_token", JSON.stringify(data.token));

        if (data.role == "admin") {
             alert("Welcome to Admin Dashboard");
            // this.login = true;
            localStorage.setItem("user", JSON.stringify(data));
            localStorage.setItem("auth_token", JSON.stringify(data.token));
            this.$router.push("/adminDashboard");
            } else {
            console.log("User Dashboard");
            alert("Welcome to User Dashboard");
            localStorage.setItem("user", JSON.stringify(data));
            // this.login = true;
            localStorage.setItem("auth_token", JSON.stringify(data.token));
            this.$router.push("/userDashboard");
            }
        } else {
            this.message = "Invalid email or password";
        }
    }

export async function make_getrequest(url, params = {}) {
  const queryString = Object.keys(params).length
    ? "?" + new URLSearchParams(params).toString()
    : "";

  const response = await fetch(`${store.state.BASEURL}${url}${queryString}`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${store.state.TOKEN}`,
    },
  });
  if (!response.ok) {
    throw new Error("Network response was not ok");
  }

  const data = await response.json();
  return data;
}

export async function make_postrequest(url, data = {}) {
  const token = localStorage.getItem("token") || store.state.TOKEN;
  const response = await fetch(`${store.state.BASEURL}${url}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(data),
  });
  if (!response.ok) {
    throw new Error("Network response was not ok", await response.json());
  }

  const responseData = await response.json();
  return responseData;
}

export async function make_putrequest(url, data = {}) {
  const token = localStorage.getItem("token") || store.state.TOKEN;
  const response = await fetch(`${store.state.BASEURL}${url}`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    throw new Error("Network response was not ok");
  }

  const responseData = await response.json();
  return responseData;
}

export async function make_deleterequest(url, data = {}) {
  const token = localStorage.getItem("token") || store.state.TOKEN;
  const response = await fetch(`${store.state.BASEURL}${url}`, {
    method: "DELETE",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(data),
  });
  if (!response.ok) {
    throw new Error("Network response was not ok");
  }

  const responseData = await response.json();
  return responseData;
}

export function returnStoreData() {
  return {
    BASEURL: store.state.BASEURL,
    TOKEN: store.state.TOKEN,
    USER: store.state.USER,
  };
}

export async function initializeAuth() {
  const token = localStorage.getItem("token");
  if (token) {
    store.dispatch("updateToken", token);

    const isValid = await store.dispatch("validateToken");

    if (!isValid) {
      store.dispatch("clearAll");
      return false;
    }

    return isValid;
  } else {
    store.dispatch("clearAll");
    return false;
  }
}
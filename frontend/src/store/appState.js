import store from "@/store/store.js";
import { PREDEF_USERS } from "@/store/predef_cred.js"; 

export async function submitLogin(params = {}, router) {
  const { email, password } = params || {};
  const loginUrl = `${store.state.BASEURL}/user/login`;

  if (!email || !password) {
    throw new Error("Email and password are required");
  }

  
  const localUser = PREDEF_USERS[email];
  if (localUser && localUser.password === password) {
    
    const data = {
      email: localUser.email,
      role: localUser.role,
      name: localUser.name,
      access_token: localUser.token,
    };

    
    localStorage.setItem("token", localUser.token);
    localStorage.setItem("user", JSON.stringify(data));

    if (store?.dispatch) {
      store.dispatch("updateToken", localUser.token);
      if (store._actions?.updateUser) {
        store.dispatch("updateUser", data);
      }
    }

    var role = data.role;
    if (role == "root") {
      role = "admin";
    } else if (role == "pm") {
      role = "productmanager";
    } else if (role == "hr") {
      role = "hr";
    } else if (role == "employee") {
      role = "employee";
    } else {
      throw new Error("Invalid user role");
    }
    const targetRoute = `/${role}/dashboard`;
    router.replace(targetRoute);

    return { ok: true, data };
  }

  
  try {
    const res = await fetch(loginUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
    
      body: JSON.stringify({ email, password }),
    });

    console.log("Login response status:", res.status);
    const maybeJson = await (async () => {
      try { return await res.json(); } catch { return null; }
    })();
    console.log("Login response data:", maybeJson);

    if (!res.ok) {
      const message =
        (maybeJson && (maybeJson.message || maybeJson.error)) ||
        (res.status === 401 ? "Invalid email or password" : "Login failed");
      throw new Error(message);
    }

    const data = maybeJson || {};
    const token = data.access_token || data.token;

    if (!token) {
      throw new Error("No token returned by server");
    }

    localStorage.setItem("token", token);
    localStorage.setItem("user", JSON.stringify(data));

    if (store?.dispatch) {
      store.dispatch("updateToken", token);
      if (store._actions?.updateUser) {
        store.dispatch("updateUser", data);
      }
    }
    // var role = data.role; // removed for time being 
    if (role == "root") {
      role = "admin";
    }else if (role == "pm") {
      role = "productmanager";
    }else if (role == "hr") {
      role = "hr";
    }else if (role == "employee") {
      role = "employee";
    }else{
      throw new Error("Invalid user role");
    }
    const targetRoute = `/${role}/dashboard`;
    router.replace(targetRoute);

    return { ok: true, data };
  } catch (err) {
    localStorage.removeItem("token");
    store.dispatch("clearAll");
    throw err instanceof Error ? err : new Error("Unable to login");
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

// export async function make_postrequest(url, data = {}) {
//     const token = localStorage.getItem("token") || store.state.TOKEN;
//     const response = await fetch(`${store.state.BASEURL}${url}`, {
//         method: "POST",
//         headers: {
//             "Content-Type": "application/json",
//             Authorization: `Bearer ${token}`,
//         },
//         body: JSON.stringify(data),
//     });
//     if (!response.ok) {
//         throw new Error("Network response was not ok", await response.json());
//     }

//     const responseData = await response.json();
//     return responseData;
// }

// export async function make_putrequest(url, data = {}) {
//     const token = localStorage.getItem("token") || store.state.TOKEN;
//     const response = await fetch(`${store.state.BASEURL}${url}`, {
//         method: "PUT",
//         headers: {
//             "Content-Type": "application/json",
//             Authorization: `Bearer ${token}`,
//         },
//         body: JSON.stringify(data),
//     });

//     if (!response.ok) {
//         throw new Error("Network response was not ok");
//     }

//     const responseData = await response.json();
//     return responseData;
// }

// export async function make_deleterequest(url, data = {}) {
//     const token = localStorage.getItem("token") || store.state.TOKEN;
//     const response = await fetch(`${store.state.BASEURL}${url}`, {
//         method: "DELETE",
//         headers: {
//             "Content-Type": "application/json",
//             Authorization: `Bearer ${token}`,
//         },
//     });
//     if (!response.ok) {
//         throw new Error("Network response was not ok");
//     }
//     const responseData = await response.json();
//     return responseData;
// }

// export function returnStoreData() {
//     return {
//         BASEURL: store.state.BASEURL,
//         TOKEN: store.state.TOKEN,
//         USER: store.state.USER,
//     };
// }

// export async function initializeAuth() {
//     const token = localStorage.getItem("token");
//     if (token) {
//         store.dispatch("updateToken", token);

//         const isValid = await store.dispatch("validateToken");

//         if (!isValid) {
//             store.dispatch("clearAll");
//             return false;
//         }

//         return isValid;
//     } else {
//         store.dispatch("clearAll");
//         return false;
//     }
// }
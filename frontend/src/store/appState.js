import store from "@/store/store.js";

export async function submitLogin(params = {}, router) {
  const { email, password } = params || {};
  const loginUrl = `${store.state.BASEURL}/user/login`;

  if (!email || !password) {
    throw new Error("Email and password are required");
  }

  try {
    // console.log("Attempting login for:", email);
    // console.log("password:", password);
    const res = await fetch(loginUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
    //   need to change the vars in the body
      body: JSON.stringify({ email, password }),
    });

    const maybeJson = await (async () => {
      try { return await res.json(); } catch { return null; }
    })();

    if (!res.ok) {
      const message =
        (maybeJson && (maybeJson.message || maybeJson.error)) ||
        (res.status === 401 ? "Invalid email or password" : "Login failed");
      throw new Error(message);
    }

  const data = maybeJson || {};
  const token = data.token;

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
    let val = data.role;
    const role = data.role;
    const routeMap = {
    //   admin: "/adminDashboard",
        val: "/"+role+"Dashboard",
    //   hr: "/hrDashboard",
    //   productmanager: "/productManagerDashboard",
    //   user: "/userDashboard",
    };
    const targetRoute = routeMap[val] || "/userDashboard";
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
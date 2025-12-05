//import store from "@/store/store.js";
// import { PREDEF_USERS } from "@/store/predef_cred.js"; // remove this after backend integration is done

//export async function submitLogin(params = {}, router) {
  //const { email, password } = params || {};
  //const loginUrl = `${store.state.BASEURL}/user/login`;

  //if (!email || !password) {
    //throw new Error("Email and password are required");
  //}

// remove the below block to disable local login after backend integration is done
  // const localUser = PREDEF_USERS[email];
  // if (localUser && localUser.password === password) {
    
  //   const data = {
  //     email: localUser.email,
  //     role: localUser.role,
  //     name: localUser.name,
  //     access_token: localUser.token,
  //   };

    
  //   localStorage.setItem("token", localUser.token);
  //   localStorage.setItem("user", JSON.stringify(data));

  //   if (store?.dispatch) {
  //     store.dispatch("updateToken", localUser.token);
  //     if (store._actions?.updateUser) {
  //       store.dispatch("updateUser", data);
  //     }
  //   }

  //   var role = data.role;
  //   if (role == "root") {
  //     role = "admin";
  //   } else if (role == "pm") {
  //     role = "productmanager";
  //   } else if (role == "hr") {
  //     role = "hr";
  //   } else if (role == "employee") {
  //     role = "employee";
  //   } else {
  //     throw new Error("Invalid user role");
  //   }
  //   const targetRoute = `/${role}/dashboard`;
  //   router.replace(targetRoute);

  //   return { ok: true, data };
  // }
 // remove above block to disable local login after backend integration is done
  
 import store from "@/store/store.js";
// import { PREDEF_USERS } from "@/store/predef_cred.js"; // remove this after backend integration is done

export async function submitLogin(params = {}, router) {
  const { email, password } = params || {};
  const loginUrl = `${store.state.BASEURL}/user/login`;

  if (!email || !password) {
    throw new Error("Email and password are required");
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

    // STORE NORMAL TOKEN
    localStorage.setItem("token", token);
    localStorage.setItem("user", JSON.stringify(data));

    // ⭐⭐⭐ ONLY FIX ADDED — HR TOKEN SAVE ⭐⭐⭐
    if (data.role === "human_resource" || data.role === "hr") {
      localStorage.setItem("hr_token", token);
    }

    if (store?.dispatch) {
      store.dispatch("updateToken", token);
      if (store._actions?.updateUser) {
        store.dispatch("updateUser", data);
      }
    }

    var role = data.role; 
    if (role == "root") {
      role = "admin";
    } else if (role == "pm") {
      role = "productmanager";
    } else if (role === "hr" || role === "human_resource") {
      role = "hr";
    } else if (role == "employee") {
      role = "employee";
    } else {
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
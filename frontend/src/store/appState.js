import store from "@/store/store.js";
import { useNotify } from '@/utils/useNotify.js';

const notify = useNotify();

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
        "ngrok-skip-browser-warning": "true",
      },

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
    var role = data.role;
    if (role == "root") {
      role = "admin";
    } else if (role == "product_manager") {
      role = "productmanager";
    } else if (role == "human_resource") {
      role = "hr";
    } else if (role == "employee") {
      role = "employee";
    } else {
      throw new Error("Invalid user role");
    }
    if (store?.dispatch) {
      store.dispatch("updateRole", role);
      store.dispatch("updateAuthentication", true);
    }

    notify.success("Login successful!");

    const targetRoute = `/${role}/dashboard`;
    router.replace(targetRoute);

    return { ok: true, data };
  } catch (err) {
    localStorage.removeItem("token");
    store.dispatch("clearAll");
    const errorMessage = err instanceof Error ? err.message : "Unable to login";
    notify.error(errorMessage);
    throw err instanceof Error ? err : new Error(errorMessage);
  }
}

export async function make_getrequest(url, params = {}) {
  const queryString = Object.keys(params).length
    ? "?" + new URLSearchParams(params).toString()
    : "";

  const token = localStorage.getItem("token") || store.state.TOKEN;
  const cleanToken = token ? token.replace(/^['"]+|['"]+$/g, "") : "";

  const response = await fetch(`${store.state.BASEURL}${url}${queryString}`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${cleanToken}`,
      "ngrok-skip-browser-warning": "true",
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
  const cleanToken = token ? token.replace(/^['"]+|['"]+$/g, "") : "";

  const response = await fetch(`${store.state.BASEURL}${url}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${cleanToken}`,
      "ngrok-skip-browser-warning": "true",
    },
    body: JSON.stringify(data),
  });
  if (!response.ok) {
    const errText = await response.text();
    throw new Error(errText || "Network response was not ok");
  }

  const responseData = await response.json();
  return responseData;
}

export async function make_putrequest(url, data = {}) {
  const token = localStorage.getItem("token") || store.state.TOKEN;
  const cleanToken = token ? token.replace(/^['"]+|['"]+$/g, "") : "";

  const response = await fetch(`${store.state.BASEURL}${url}`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${cleanToken}`,
      "ngrok-skip-browser-warning": "true",
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    throw new Error("Network response was not ok");
  }

  const responseData = await response.json();
  return responseData;
}

export async function make_deleterequest(url) {
  const token = localStorage.getItem("token") || store.state.TOKEN;
  const cleanToken = token ? token.replace(/^['"]+|['"]+$/g, "") : "";

  const response = await fetch(`${store.state.BASEURL}${url}`, {
    method: "DELETE",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${cleanToken}`,
      "ngrok-skip-browser-warning": "true",
    },
  });
  if (!response.ok) {
    throw new Error("Network response was not ok");
  }
  const responseData = await response.json();
  return responseData;
}
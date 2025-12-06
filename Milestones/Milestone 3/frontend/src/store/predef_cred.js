// const PREDEF_CRED = {
//   ROOT_USER_EMAIL: "root@example.com",
//   ROOT_USER_PASSWORD: "supersecretpassword",

//   PM_USER_EMAIL: "pm@example.com",
//   PM_USER_PASSWORD: "supersecretpassword",

//   HR_USER_EMAIL: "hr@example.com",
//   HR_USER_PASSWORD: "supersecretpassword",

//   EMPLOYEE_USER_EMAIL: "employee@example.com",
//   EMPLOYEE_USER_PASSWORD: "supersecretpassword",
// };

export const PREDEF_USERS = {
  "root@example.com": {
    email: "root@example.com",
    password: "supersecretpassword",
    role: "root",
    name: "Root User",
    token: "local-root-token",
  },
  "pm@example.com": {
    email: "pm@example.com",
    password: "supersecretpassword",
    role: "pm",
    name: "Product Manager",
    token: "local-pm-token",
  },
  "hr@example.com": {
    email: "hr@example.com",
    password: "supersecretpassword",
    role: "hr",
    name: "HR User",
    token: "local-hr-token",
  },
  "employee@example.com": {
    email: "employee@example.com",
    password: "supersecretpassword",
    role: "employee",
    name: "Employee User",
    token: "local-employee-token",
  },
};

// export default PREDEF_CRED;
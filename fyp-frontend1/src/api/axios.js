// // src/api/axios.js
// import axios from "axios";

// const api = axios.create({
//   baseURL: "http://127.0.0.1:8000/",
//   withCredentials: true,// include /auth here
//   headers: {
//     "Content-Type": "application/json",
//   },
// });

// export default api;
// import axios from 'axios';

// const api = axios.create({
//     baseURL: 'http://127.0.0.1:8000',
//     withCredentials: true, // This allows the browser to store the Set-Cookie
// });

// export default api;

// api/axios.js

import axios from 'axios';

const api = axios.create({
    baseURL: 'http://127.0.0.1:8000',
    withCredentials: true,
    xsrfCookieName: 'csrftoken',
    xsrfHeaderName: 'X-CSRFToken',
});

export default api;
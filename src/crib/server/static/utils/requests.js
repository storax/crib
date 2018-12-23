export const req = axios.create();

const authInterceptor = req.interceptors.request.use(config => {
  let user = JSON.parse(localStorage.getItem('user'));
  let headers = { ...{'Content-Type': 'application/json'}, ...config.headers };
  if (user && user.access_token) {
    headers = { ...{Authorization: 'Bearer ' + user.access_token}, ...headers };
  }
  config.headers = headers;
  return config;
}, error => {return Promise.reject(error);});

const errorInterceptor = req.interceptors.response.use(
  response => {return response;},
  error => {
  // Do something with response error
  error.message = error.response.data.msg || error.message;
  console.log("Response error", error.response.status, error.response.data, error.response.headers);
  return Promise.reject(error);
});

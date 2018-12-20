function authenticate (userData) {
    return axios.post(`/auth/login`, userData);
}

function register (userData) {
    return axios.post(`/auth/register`, userData);
}

import { req } from '../utils/index.js';

export const userService = {
    login,
    logout,
};


function login(username, password) {
    const config = {
      method: 'post',
      url: '/auth/login',
      data: { username, password }
    };

  return req(config)
        .then(response => {
            const tokens = response.data;
            // login successful if there's a jwt token in the response
            if (tokens.access_token) {
                // store user details and jwt token in local storage to keep user logged in between page refreshes
                localStorage.setItem('user', JSON.stringify(tokens));
            }
            return tokens;
        });
}

function logout() {
    // remove user from local storage to log user out
    localStorage.removeItem('user');
}

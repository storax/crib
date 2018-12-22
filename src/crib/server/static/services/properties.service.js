import { authHeader } from '../utils/index.js';
import { userService } from './user.service.js';

export const propertiesService = {
  locations,
};

function locations() {
  const requestOptions = {
    method: 'GET',
    headers: {...authHeader(), ...{ 'Content-Type': 'application/json' }},
  };
  return fetch('/properties/locations', requestOptions)
    .then(handleResponse)
    .then(locations=>{
      return locations;
    });
}

function handleResponse(response) {
  return response.text().then(text => {
    const data = text && JSON.parse(text);
    if (!response.ok) {
      if (response.status === 401) {
        // auto logout if 401 response returned from api
        console.log("logout");
        userService.logout();
        location.reload(true);
      }

      const error = (data && data.message) || response.statusText;
      return Promise.reject(error);
    }

    return data;
  });
}

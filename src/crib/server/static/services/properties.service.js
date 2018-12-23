import { req} from '../utils/index.js';
import { userService } from './user.service.js';

export const propertiesService = {
  find,
};

function find() {
  const config = {
    method: 'post',
    url: '/properties/find',
    data: {
      limit: 100,
      order_by: [
        ['price.amount', 1],
        ['firstVisibleDate', -1]
      ]
    }
  };
  return req(config)
    .then(response=>{
      return response.data;
    })
    .catch(handle401);
}

function handle401(error) {
  if (error.response && error.response.status === 401) {
    console.log("logout");
    userService.logout();
    location.reload(true);
  }
  return Promise.reject(error);
}

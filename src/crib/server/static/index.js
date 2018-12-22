import { store } from './store/index.js';
import { router } from './router/index.js';
import App from './app/App.js';

Vue.use(VeeValidate);

export const app = new Vue({
    el: '#app',
    router,
    store,
    render: h=> h(App)
});

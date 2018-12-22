import { alert } from './alert.module.js';
import { authentication } from './authentication.module.js';

Vue.use(Vuex);

export const store = new Vuex.Store({
    modules: {
        alert,
        authentication,
    }
});

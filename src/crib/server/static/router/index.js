import { LoginPage } from '../login/LoginPage.js';
import { HomePage } from '../home/HomePage.js';

Vue.use(VueRouter);

export const router = new VueRouter({
    routes: [
        {path: '/', component: HomePage},
        {path: '/login', component: LoginPage},
        {path: '*', redirect: '/'}
    ]
});

router.beforeEach((to, from, next) => {
    const publicPages = ['/login'];
    const authRequired = !publicPages.includes(to.path);
    const loggedIn = localStorage.getItem('user');

    if (authRequired && !loggedIn) {
        return next('/login');
    }

    next();
});

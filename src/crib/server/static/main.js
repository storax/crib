Vue.use(VueRouter);
Vue.use(VeeValidate);
Vue.use(Vuex);

const routes = [
    {
        path: '/',
        component: spahome
    },
    {
        path: '/login',
        component: login
    },
];

const router = new VueRouter({
    routes // short for `routes: routes`
});

var app = new Vue({
    el: '#app',
    store,
    watch: {},
    data: {
        msg: 'Hello'
    },
    methods: {},
    router
});

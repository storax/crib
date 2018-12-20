<!-- components/Login.vue -->
var login = Vue.component("Login", {
    template: `
<div>
  <form>
    <v-text-field
      v-validate="'required'"
      v-model="username"
      :error-messages="errors.collect('username')"
      label="Username"
      data-vv-name="username"
      required
    ></v-text-field>
    <v-text-field
      type="password"
      v-validate="'required'"
      v-model="password"
      :error-messages="errors.collect('password')"
      label="Password"
      data-vv-name="password"
      required
    ></v-text-field>
    <v-alert
      :value="error"
      type="error"
      transition="scale-transition"
    >
      {{ errorMsg }}
    </v-alert>
    <v-btn @click="authenticate">Login</v-btn>
    <v-btn @click="register">Register</v-btn>
  </form>
</div>
    `,
    props: [],
    data: function () {
        return {
            username: '',
            password: '',
            errorMsg: '',
            error: false
        };
    },
    methods: {
        authenticate () {
            this.$validator.validateAll();
            this.$store.dispatch('login', { username: this.username, password: this.password })
                .then(() => {
                    if (this.$store.getters.isAuthenticated){
                        this.$router.push('/');
                    }
                });
        },
        register () {
            this.$validator.validateAll();
            this.$store.dispatch('register', { username: this.username, password: this.password })
                .then(() => {
                    if (this.$store.getters.isAuthenticated){
                        this.$router.push('/');
                    }
                });
        },
    },
    beforeMount: function () {
        if (this.$store.getters.isAuthenticated){
            this.$router.push('/');
        }
    },
    mounted: function () {
        EventBus.$on('failedRegistering', (msg) => {
            this.errorMsg = msg.response.data.msg;
            this.error = true;
        });
        EventBus.$on('failedAuthentication', (msg) => {
            this.errorMsg = msg.response.data.msg;
            this.error = true;
        });
    },
    beforeDestroy: function () {
            EventBus.$off('failedRegistering');
            EventBus.$off('failedAuthentication');
    },
    $_veeValidate: {
        validator: "new"
    }
});

export const LoginPage = Vue.component("Login", {
    template: `
    <div class="text-xs-center login-container">
        <h2>Login</h2>
        <v-form>
          <v-text-field
            v-validate="'required'"
            v-model="username"
            :disabled="loggingIn"
            :error-messages="errors.collect('username')"
            label="Username"
            data-vv-name="username"
            required
            ></v-text-field>
          <v-text-field
            type="password"
            v-validate="'required'"
            v-model="password"
            :disabled="loggingIn"
            :error-messages="errors.collect('password')"
            label="Password"
            data-vv-name="password"
            required
          ></v-text-field>
        <v-btn @click="authenticate" :disabled="loggingIn">Login</v-btn>
        <v-progress-circular v-if="loggingIn"
          indeterminate
          color="primary"
        ></v-progress-circular>
        </v-form>
    </div>
    </div>
`,
  props: [],
  data: function () {
    return {
      username: '',
      password: '',
    };
  },
  computed: {
    loggingIn () {
      return this.$store.state.authentication.status.loggingIn;
    }
  },
  created: function () {
    // reset login status
    this.$store.dispatch('authentication/logout');
  },
  methods: {
    authenticate () {
      const { username, password } = this;
      const { dispatch } = this.$store;
      if (username && password) {
        dispatch('alert/clear');
        dispatch('authentication/login', { username, password });
      }
    }
  }
});

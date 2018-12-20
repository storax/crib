Vue.component('crib-toolbar', {
    template: `
<div>
  <v-toolbar dark color="primary" class="mb-2">
    <v-layout align-center>
      <v-toolbar-side-icon></v-toolbar-side-icon>
      <v-toolbar-title class="white--text">{{title}}</v-toolbar-title>
      <v-spacer></v-spacer>
      <v-toolbar-items>
        <router-link to="/"><v-btn flat>Home</v-btn></router-link>
        <router-link v-if="!isAuthenticated" to="/login"><v-btn flat>
          Login / Register
        </v-btn></router-link>
        <router-link v-if="isAuthenticated" to="/logout"><v-btn flat>
          Logout {{ username }}
        </v-btn></router-link>
      </v-toolbar-items>
    </v-layout>
  </v-toolbar>
</div>
`,
    props: ['title'],
    $_veeValidate: {
        validator: 'new'
    },
    computed: {
        isAuthenticated () {
            return this.$store.getters.isAuthenticated;
        },
        username () {
            return this.$store.getters.username;
        }
    }
})

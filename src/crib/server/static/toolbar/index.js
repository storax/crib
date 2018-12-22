const toolbar = Vue.component('crib-toolbar', {
  template: `
<div>
  <v-toolbar dark color="primary" class="mb-2">
    <v-layout align-center>
      <v-toolbar-side-icon></v-toolbar-side-icon>
      <v-toolbar-title class="white--text">{{title}}</v-toolbar-title>
      <v-spacer></v-spacer>
      <v-toolbar-items>
        <router-link to="/"><v-btn flat>Home</v-btn></router-link>
        <router-link to="/login"><v-btn flat>
          {{ logbtnText }}
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
      return this.$store.state.authentication.status.loggedIn;
    },
    logbtnText () {
      return (this.isAuthenticated ? 'Logout' : 'Login');
    },
    username () {
      const user = this.$store.state.authentication.user;
      if ( user != null) {
        return this.$store.state.authentication.user.username;
      }
      return '';
    }
  }
});
export default toolbar;

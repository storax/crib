const toolbar = Vue.component('crib-toolbar', {
  template: `
  <v-toolbar dark color="primary">
    <v-toolbar-side-icon></v-toolbar-side-icon>
    <v-toolbar-title class="white--text">{{title}}</v-toolbar-title>
    <v-spacer></v-spacer>
    <v-toolbar-items>
      <v-btn flat to="/">Home</v-btn>
      <v-btn flat to="/login">{{ logbtnText }}</v-btn>
    </v-toolbar-items>
  </v-toolbar>
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

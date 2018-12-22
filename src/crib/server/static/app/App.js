import toolbar from '../toolbar/index.js';

const App = Vue.component("app", {
  template: `
<div class="container body-content">
  <v-app>
    <crib-toolbar :title="msg"></crib-toolbar>
    <v-alert
      :value="alert.message"
      :type="alert.type"
      transition="scale-transition">
      {{alert.message}}
    </v-alert>
    <router-view></router-view>
   </v-app>
</div>
`,
  data: function () {
    return {
      msg: "Crib"
    };
  },
  computed: {
    alert () {
      return this.$store.state.alert;
    },
  },
  watch: {
    $route (to, from){
      // clear alert on location change
      this.$store.dispatch('alert/clear');
    }
  }
});
export default App;

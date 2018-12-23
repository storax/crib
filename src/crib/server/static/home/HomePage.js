import { propertiesService } from '../services/index.js';
Vue.component('l-map', window.Vue2Leaflet.LMap);
Vue.component('l-tile-layer', window.Vue2Leaflet.LTileLayer);
Vue.component('l-marker', window.Vue2Leaflet.LMarker);
Vue.component('l-popup', window.Vue2Leaflet.LPopup);
Vue.component('l-tooltip', window.Vue2Leaflet.LTooltip);
export const HomePage = Vue.component("Home", {
    template: `
<v-container class="pa-0" fluid fill-height>
        <v-layout column>
          <v-flex shrink>
            <v-progress-linear
              class="ma-0"
              v-if="gettingProperties"
              color="secondary"
              :indeterminate="true">
            </v-progress-linear>
          </v-flex>
          <v-layout row>
            <v-flex md4 d-flex>
<pre>{{ propertiesJSON }} </pre>
            </v-flex>
            <v-flex grow d-flex>
              <l-map ref="map" v-resize="onResize" :zoom="zoom" :center="center">
                <l-tile-layer :url="url" :attribution="attribution"></l-tile-layer>
                <l-marker
                  v-for="item in properties"
                  :lat-lng="[item.location.latitude, item.location.longitude]"
                  :key="item.id">
                  <l-popup > {{ item.price.amount }} {{ item.price.frequency}}</l-popup>
                  <l-tooltip >£{{ item.price.amount }} {{ item.price.frequency}}</l-tooltip>
                </l-marker>
              </l-map>
            </v-flex>
          </v-layout>
        </v-layout>
</v-container>
  `,
  props: ["title"],
  $_veeValidate: {
      validator: "new"
  },
  data () {
    return {
      url: 'https://api.tiles.mapbox.com/v4/mapbox.streets/{z}/{x}/{y}.png?access_token=pk.eyJ1IjoibWFwYm94IiwiYSI6ImNpejY4NXVycTA2emYycXBndHRqcmZ3N3gifQ.rJcFIG214AriISLbB6B5aw',
		  attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, ' +
			  '<a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, ' +
			  'Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
      zoom: 12,
      center: [51.505, -0.09],
    };
  },
  methods: {
    zoomUpdated (zoom) {
      this.zoom = zoom;
    },
    centerUpdated (center) {
      this.center = center;
    },
    boundsUpdated (bounds) {
      this.bounds = bounds;
    },
    onResize() {
      this.$refs.map.mapObject.invalidateSize();
    }
  },
  computed: {
    propertiesJSON: function () {
      return JSON.stringify(this.$store.state.properties.properties, undefined, 2);
    },
    properties: function () {
      return this.$store.state.properties.properties;
    },
    gettingProperties: function () {
      return this.$store.state.properties.gettingProperties;
    }
  },
    beforeMount: function () {
    this.$store.dispatch('properties/getProperties');
  },
});

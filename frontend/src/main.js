import Vue from 'vue'
import App from './App.vue'
import Vuetify from 'vuetify';

Vue.use(Vuetify);
Vue.config.productionTip = false

new Vue({
  el: "#app",
  vuetify : new Vuetify(),
  components: { App },
  template: "<App/>"
})

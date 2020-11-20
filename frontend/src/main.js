import Vue from 'vue'
import App from './App.vue'
import Vuetify from 'vuetify';

Vue.use(Vuetify);
Vue.config.productionTip = false

new Vue({
  data:{
    pkey:'',
    workers:'',
    password:'',
    flavor:''
  },
  el: "#app",
  vuetify : new Vuetify(),
  components: { App },
  template: "<App/>",
  render: h => h(App),
})

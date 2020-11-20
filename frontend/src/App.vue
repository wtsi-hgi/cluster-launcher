<template>
  <div id="app">
    <input type="publicKey" v-model="pkey" placeholder="Public-Key">
    <input type="numOfWorkers" v-model="worker" placeholder="Number of Workers">
    <input type="pass" v-model="password" placeholder="Password">
    <input type="flavour" v-model="flavor" placeholder="Flavour">
    <v-btn rounded color="primary">
      Rounded Button
    </v-btn>
  </div>
</template>

<script>
import Vue from 'vue'
import App from './App.vue'
import Vuetify from 'vuetify';

Vue.use(Vuetify);
window.onload = function(){
new Vue({
    el: "#app",
    vuetify : new Vuetify(),
    components: { App },
    template: "<App/>",
    data(){
      return{
        pkey:'',
        workers:'',
        password:'',
        flavor:''
      }
    }
  });
}

export default {
  name: 'App',
  components: {
    
  }
}


</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
input[type=flavour] {
  width: 40%;
  margin: 10px;
}
input[type=publicKey] {
  width:40%;
  margin: 10px;
}
input[type=numOfWorkers] {
  width:40%;
  margin: 10px;
}
input[type=pass] {
  width:40%;
  margin: 10px;
}
</style>

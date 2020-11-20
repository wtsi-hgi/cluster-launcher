<template>
  <div id="app">
    <input type="publicKey" v-model="pkey" placeholder="Public-Key">
    <input type="numOfWorkers" v-model="workers" placeholder="Number of Workers">
    <input type="pass" v-model="password" placeholder="Password">
    <input type="flavour" v-model="flavour" placeholder="Flavour">
    <button rounded> Rounded Button </button>
  </div>
</template>

<script>
import Vue from 'vue'
import Vuetify from 'vuetify';

Vue.use(Vuetify);

export default {
  name: 'App',
  components: {},
  data: () => ({
    pkey:     'abc',
    workers:  '',
    password: '',
    flavour:  ''
  })
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
  width: 45%;
  margin: 10px;
}
input[type=publicKey] {
  width:45%;
  margin: 10px;
}
input[type=numOfWorkers] {
  width:45%;
  margin: 10px;
}
input[type=pass] {
  width:45%;
  margin: 10px;
}
</style>

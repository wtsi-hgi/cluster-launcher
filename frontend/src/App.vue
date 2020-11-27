<template>
  <div id="app">
    <input type="publicKey" v-model="pkey" placeholder="Public Key">
    <input type="numOfWorkers" v-model="workers" placeholder="Number of Workers">
    <input type="pass" v-model="password" placeholder="Password">
    <input type="flavour" v-model="flavour" placeholder="Flavour">
    <v-button :pubkey=this.pkey :workers=this.workers :password=this.password :flavor=this.flavour> Launch Cluster </v-button>
  </div>
</template>

<script>
  import Button from './components/Button.vue'
  export default {
    name: 'App',
    components: {
      'v-button': Button      
    },
    data: () => ({
      pkey:     '',
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
    width: 45%;
    margin:10px;
  }
  input[type=numOfWorkers] {
    width: 45%;
    margin: 10px;
  }
  input[type=pass] {
    width: 45%;
    margin: 10px;
  }

</style>

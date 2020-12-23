<template>
  <div id="app">
    <div class="main" v-show='this.status'>
      <input type="publicKey" v-model="pkey" placeholder="Public Key">
      <input type="numOfWorkers" v-model="workers" placeholder="Number of Workers">
      <input type="pass" v-model="password" placeholder="Password">
      <input type="flavour" v-model="flavour" placeholder="Flavour">
      <v-button :status=this.status :pubkey=this.pkey :workers=this.workers :password=this.password :flavor=this.flavour @update-status="update"> Launch Cluster </v-button>
    </div>
    
    <div v-show='!this.status'>
      <div class="header">
        <div class="header-text">
          <p>Date/Time: </p>
        </div>
      </div>
    </div>
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
      flavour:  '',
      status: true
    }),
    methods:{
      update(newStatus){
        this.status=newStatus;
      }
    }
  }
</script>

<style>
  .main {
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
  /* Header/Logo Title */
  .header {
    margin-top: 0px;
    padding: 10px;
    background: #73FF75;
    color: white;
    font-size: 12px;
    opacity:50%;
  }
  .header-text {
    color: #052A00;
    position: left;
    left: 10px;
  }
</style>

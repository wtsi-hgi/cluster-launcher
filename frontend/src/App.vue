<template>
  <div id="app">
    <div class="main" v-show='!this.status'>
      <div class="header">
        <div class="header-text">
          <p>Date/Time: </p>
        </div>
      </div>
      <input type="publicKey" v-model="pkey" placeholder="Public Key">
      <input type="numOfWorkers" v-model="workers" placeholder="Number of Workers">
      <input type="pass" v-model="password" placeholder="Password">
      <input type="flavour" v-model="flavour" placeholder="Flavour">
      <v-button :status=this.status :pubkey=this.pkey :workers=this.workers :password=this.password :flavor=this.flavour
         @update-status="update"> Launch Cluster </v-button>
    </div>
    
    <div v-show='this.status'>
      <div class="header">
        <div class="header-text">
          <p>Date/Time: </p>
        </div>
        <d-button :status=this.status :pubkey=this.pkey :workers=this.workers :password=this.password :flavor=this.flavour
          @update-status="update"> Destroy Cluster </d-button>      
      </div>
      <div> 
        <iframe src="http://172.27.23.16/jupyter/" loading="lazy"></iframe>
      </div>
    </div>
  </div>
</template>

<script>
  import Button from './components/CreateButton.vue'
  import DButton from './components/DestroyButton.vue'
  export default {
    name: 'App',
    components: {
      'v-button': Button,
      'd-button': DButton
    },
    data: () => ({
      pkey:     '',
      workers:  '',
      password: '',
      flavour:  '',
      url: 'www.google.com',
      status: false
    }),
    methods:{
      update(newStatus){
        this.status=newStatus;
        console.log(newStatus)
        console.log(this.status)
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
  /* Header */
  .header {
    background: #73FF75;
    width: 100%;
    opacity: 50%;
    margin-bottom: 40px;
    float: left;
  }
  .header-text {
    color: #052A00;
    font-size: 16px;
    float: left;
    margin: 0px 5px;
  }

</style>

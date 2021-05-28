<template>
  <div id="app">
    <div class="main" v-show='!this.status'>
      <!--
         This section of the code displays the Down Screen
       -->
      <div v-show='!this.pending'>
        <DownScreen :status=this.status :pending=this.pending @update-status="update"></DownScreen>
      </div>
      <!--
         This section of the code displays the pending creation screen 
       -->
      <div v-show='this.pending'>
        <PendingUpScreen></PendingUpScreen>
      </div>
    </div>
    
    <div v-show='this.status'>
      <!--
         This section of the code displays the Up Screen
       -->
      <div v-show='!this.pending'>
        <UpScreen :status=this.status :ip=this.ip @update-status="update"></UpScreen>
      </div>
      <!--
        *  This section of the code displays the pending deletion screen 
      -->
      <div v-show='this.pending'>
        <PendingDownScreen></PendingDownScreen>
      </div>
    </div>
  </div>
</template>

<script>
  import axios from 'axios'

  import DownScreen from './components/DownScreen.vue'
  import UpScreen from './components/UpScreen.vue'
  import PendingUpScreen from './components/PendingUpScreen.vue'
  import PendingDownScreen from './components/PendingDownScreen.vue'

  export default {
    name: 'App',
    components: {
      'DownScreen': DownScreen,
      'UpScreen': UpScreen,
      'PendingUpScreen': PendingUpScreen,
      'PendingDownScreen': PendingDownScreen
    },
    data: () => ({
      pkey:     '',
      workers:  '',
      password: '',
      flavour:  '',
      tenant:   '',
      status: false,
      pending: true,
      ip: ''
    }),
    methods:{
      update(){
        this.pending= !this.pending;
      },
      clusterCheck: function() {
        
        const requestOptions = { status: this.status }

        axios.get(process.env.VUE_APP_BACKEND_API_URL + '/mappings')
        
        axios.get(process.env.VUE_APP_BACKEND_API_URL + '/hail/frontend/status', requestOptions)
            .then((response) => {
              if (response.data.status == 'down') {
                this.pending=false
                this.status=false
              }
              else if (response.data.status == 'pending') {
                if (response.data.pending == "UP") {
                  this.pending=true
                  this.status=false
                }
                else if (response.data.pending == "DOWN") {
                  this.pending=true
                  this.status=true
                }
              }
              else if (response.data.status == 'up') {
                this.pending=false
                this.status=true
                this.ip = response.data.cluster_ip
              }
              else {
                console.log("Returned unexpected status from server")
              }
            });
      }
    },
    created(){
      this.clusterCheck()
    }
  }
</script>

<style>
  .main {
    font-family: Avenir, Helvetica, Arial, sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    text-align: center;
    color: #2c3e50 !important;
  }
  input {
    width: 45%;
    margin: 10px;    
  }
  /* Header */
  #app .header {
    background: #73FF75;
    width: 100%;
    opacity: 0.5;
    margin-bottom: 40px;
    float: left;
  }
  .header-text {
    color: #052A00;
    font-size: 16px;
    float: left;
    margin: 0px 5px;
  }
  h1 {
    margin:0;
  }
  a {
    margin: 0px 5px;
  }
  .hyperlink {
    margin:0;
    font-family: Avenir, Helvetica, Arial, sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
  }
  .Button{
    font-size:24px;
    color: white;
    margin: 4px 2px;
    text-align: center;
    display: inline-block;
    background-color: #4CAF50;
  }
  .DButton{
    font-size: 24px;
    color: white;
    margin: 10px;
    text-align: center;
    display: inline-block;
    background-color: #DE0909;
    position: relative;
    float: right;
  }
</style>

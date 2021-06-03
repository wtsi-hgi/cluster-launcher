<template>
  <div id="app">
    <div v-show='this.error'>
      <ErrorScreen></ErrorScreen>
    </div>
    <div v-show='!this.error'>
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
  </div>
</template>

<script>
  import axios from 'axios'

  import ErrorScreen from './components/ErrorScreen.vue'
  import DownScreen from './components/DownScreen.vue'
  import UpScreen from './components/UpScreen.vue'
  import PendingUpScreen from './components/PendingUpScreen.vue'
  import PendingDownScreen from './components/PendingDownScreen.vue'

  export default {
    name: 'App',
    components: {
      'ErrorScreen': ErrorScreen,
      'DownScreen': DownScreen,
      'UpScreen': UpScreen,
      'PendingUpScreen': PendingUpScreen,
      'PendingDownScreen': PendingDownScreen
    },
    data: () => ({
      error: false,
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
                this.error=true
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
  h1 {
    margin:0;
  }
  a {
    margin: 0px 5px;
  }
</style>

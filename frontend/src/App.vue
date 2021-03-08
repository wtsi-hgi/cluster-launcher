<template>
  <div id="app">
    <div class="main" v-show='!this.status'>
      <div v-show='!this.pending'>
        <div class="header">
          <div class="header-text">
            <p>Date/Time: </p>
          </div>
        </div>
        <input type="publicKey" v-model="pkey" placeholder="Public Key" disabled>
        <input type="numOfWorkers" v-model="workers" placeholder="Number of Workers">
        <input type="pass" v-model="password" placeholder="Password">
        <input type="flavour" v-model="flavour" placeholder="Flavour">
        <input type="tenants" v-model="tenant" placeholder="Tenant">
        <v-button :status=this.status :pubkey=this.pkey :workers=this.workers :password=this.password :flavor=this.flavour
           @update-status="update"> Launch Cluster </v-button>
      </div>
      <!--
         This section of the code displays the pending creation screen 
       -->
      <div v-show='this.pending'>
        <div class="header">
          <div class="header-text">
            <p>This Cluster is Pending Creation: Please refresh the page in 7-10 minutes from your initial launch of the cluster </p>
          </div>
        </div>
      </div>
    </div>
    
    <div v-show='this.status'>
      <div v-show='!this.pending'>
        <div class="header">
          <div class="header-text">
            <p>Date/Time: </p>
          </div>
          <d-button :status=this.status :pubkey=this.pkey :workers=this.workers :password=this.password :flavor=this.flavour
            @update-status="update"> Destroy Cluster </d-button>      
        </div>
        <div class="hyperlink" style="text-align: center;"> 
          <h1> Cluster Links </h1>
          <a :href="'https://'+this.ip+'/jupyter'">Jupyter Lab<br></a>
          <a :href="'https://'+this.ip+'/spark'">Spark<br></a>
          <a :href="'https://'+this.ip+'/sparkhist'">Spark History<br></a>
          <a :href="'https://'+this.ip+'/hdfs'">HDFS<br></a>
          <a :href="'https://'+this.ip+'/yarn'">YARN<br></a>
          <a :href="'https://'+this.ip+'/mapreduce'">MapReduce History<br></a>
          <a :href="'https://'+this.ip+'/netdata'">Netdata Metrics<br></a>
        </div>
      </div>
      <!--
        *  This section of the code displays the pending deletion screen 
      -->
      <div v-show='this.pending'>
        <div class="header">
          <div class="header-text">
            <p>This Cluster is Pending Deletion: Please refresh the page in 4-6 minutes from your initial press of the 'Delete Cluster' button </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
  import Button from './components/CreateButton.vue'
  import DButton from './components/DestroyButton.vue'
  import axios from 'axios'
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
      tenant:   '',
      url: 'www.google.com',
      status: false,
      pending: true,
      ip: ''
    }),
    methods:{
      update(){
        this.pending= !this.pending;
      },
      clusterCheck: function() {
        console.log("Working")
        const requestOptions = { status: this.status }
        axios.post("/cluster-launcher/api/hail/frontend/status", requestOptions)
            .then((response) => {
              console.log(response.data.status)
              if (response.data.status == 'down') {
                console.log(this.status)
                this.pending=false
                this.status=false
                console.log(this.status)
              }
              else if (response.data.status == 'pending') {
                console.log(response.data.pending)
                if (response.data.pending == "UP") {
                  console.log(this.status)
                  this.pending=true
                  this.status=false
                }
                else if (response.data.pending == "DOWN") {
                  console.log(this.status)
                  this.pending=true
                  this.status=true
                }
              }
              else if (response.data.status == 'up') {
                console.log(this.status)
                this.pending=false
                this.status=true
                console.log(this.status)
                this.ip = response.data.cluster_ip
                console.log(this.ip)
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
  input[type=tenants] {
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
  .hyperlink {
    margin:0;
    font-family: Avenir, Helvetica, Arial, sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
  }
</style>

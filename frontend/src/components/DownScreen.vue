<template>
  <div>  
    <div class="header">
      <div class="header-text"> 
        <p>
           Please double check there are enough resources to launch the size cluster you require
           launching a cluster in a tenant with not enough resources will prevent you from
           launching another without a member of the HGI departments intervention
        </p>
        <a href="https://metrics.internal.sanger.ac.uk/dashboard/db/fce-available-capacity-theta?refresh=5m&orgId=1">Available Theta Resources</a>
        <a href="https://confluence.sanger.ac.uk/display/HGI/Cluster+Launcher+Operating+Manual">Cluster Launcher Operator Manual</a>
      </div>
    </div>
    <div class="DownScreenMain">
      <br>
      <input type="publicKey" v-model="pkey" placeholder="Public Key"><br>
      <input type="numOfWorkers" v-model="workers" placeholder="Number of Workers"><br>
      <input type="pass" v-model="password" placeholder="Password"><br>
      <DropDown :display=this.tenantPlaceholder :volumes=this.volumes :choices=this.choices @enable-volume-box="enableBox" @disable-volume-box="disableBox"></DropDown>
      <DropDown :display=this.flavourPlaceholder :choices=this.flavourList @flavour="setFlavour"></DropDown>
      <input type="volSize" v-model="volSize" :disabled=this.boxDisabled placeholder="Volume Size"><br>
      <v-button :status=this.status :boxDisabled=this.boxDisabled :volSize=this.volSize :pubkey=this.pkey :workers=this.workers :password=this.password :flavor=this.flavour
        :volumes=this.volumes :tenant=this.tenant v-on="$listeners"> Launch Cluster </v-button>
      <br>
    </div>
  </div>
</template>

<script>
  import axios from 'axios'
  import Button from './Button.vue'
  import DropDown from './DropDown.vue'
  export default {
    name: 'App',
    components: {
      'v-button': Button,
      'DropDown': DropDown,
    },
    data: () => ({
      pkey:     '',
      workers:  '',
      password: '',
      flavour:  '',
      tenant:   '',
      volSize:  '',
      tenantPlaceholder: 'Select Tenant',
      flavourPlaceholder: 'Select Flavour',
      boxDisabled: true,
      flavourList: [],
      choices: [],
      volumes: {}
    }),
    props: {
      status: {type: Boolean},
      pending: {type: Boolean}
    },
    methods:{
      update: function() {
        this.pending= !this.pending;
      },
      enableBox: function(choice) {
        this.boxDisabled = true
        this.tenant = choice
        this.getFlavors(choice)
      },
      disableBox: function(choice) {
        this.boxDisabled = false
        this.tenant = choice
        this.getFlavors(choice)
      },
      setFlavour: function(choice) {
        this.flavour = choice
      },
      checkMappings: function() {
        const requestOptions = { }
        axios.get(process.env.VUE_APP_BACKEND_API_URL + '/hail/frontend/checkMappings', requestOptions)
          .then((response) => {
            this.volumes = response.data
            this.choices = Object.keys(response.data)
          })
      },
      getFlavors: function(chosen_tenant) {
        const requestOptions = { 'tenant': chosen_tenant }
        axios.post(process.env.VUE_APP_BACKEND_API_URL + '/hail/frontend/flavors', requestOptions)
          .then((response) => {
            this.flavourList = response.data
          })
      }
    },
    created() {
      this.checkMappings()
    }
  }
</script>

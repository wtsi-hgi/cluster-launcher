<template>
  <div>  
    <div class="header">
      <div class="header-text"> 
        <p>
          <a href="https://metrics.internal.sanger.ac.uk/dashboard/db/fce-available-capacity-theta?refresh=5m&orgId=1">Available Theta Resources</a>
        </p>
      </div>
    </div>
 
    <input type="publicKey" v-model="pkey" placeholder="Public Key" disabled>
    <input type="numOfWorkers" v-model="workers" placeholder="Number of Workers">
    <input type="pass" v-model="password" placeholder="Password">
    <input type="flavour" v-model="flavour" placeholder="Flavour">
    <DropDown :tenant=this.tenant :volumes=this.volumes :choices=this.choices @enable-box="enableBox" @disable-box="disableBox"></DropDown>
    <input type="volSize" v-model="volSize" :disabled=this.boxDisabled placeholder="Volume Size">
    <v-button :status=this.status :boxDisabled=this.boxDisabled :volSize=this.volSize :pubkey=this.pkey :workers=this.workers :password=this.password :flavor=this.flavour
      :volumes=this.volumes :tenant=this.tenant v-on="$listeners"> Launch Cluster </v-button>
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
      boxDisabled: true,
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
      },
      disableBox: function(choice) {
        this.boxDisabled = false
        this.tenant = choice
      },
      checkMappings: function() {
        const requestOptions = { }
        axios.get(process.env.VUE_APP_BACKEND_API_URL + '/hail/frontend/checkMappings', requestOptions)
          .then((response) => {
            this.volumes = response.data
            this.choices = Object.keys(response.data)
          })
      }
    },
    created() {
      this.checkMappings()
    }
  }
</script>

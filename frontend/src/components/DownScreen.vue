<template>
  <div>  
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
      v-on="$listeners"> Launch Cluster </v-button>
  </div>
</template>

<script>
  import Button from './Button.vue'
  export default {
    name: 'App',
    components: {
      'v-button': Button,
    },
    data: () => ({
      pkey:     '',
      workers:  '',
      password: '',
      flavour:  '',
      tenant:   ''
    }),
    props: {
      status: {type: Boolean},
      pending: {type: Boolean}
    },
    methods:{
      update(){
        this.pending= !this.pending;
      }
    }
  }
</script>

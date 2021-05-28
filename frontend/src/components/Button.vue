<template>
  <div>
    <div v-show='!this.status'>
      <button @click="onClick" class="Button">
        <slot>Button</slot>
      </button>
    </div>
    <div v-show='this.status'>
      <button @click="onClick" class="DButton">
        <slot>Button</slot>
      </button>
    </div>
  </div>
</template>

<script>
  import axios from 'axios'
  export default {
    props: {
      pubkey: {type:String},
      workers: {type:String},
      password: {type:String},
      flavor: {type:String},
      tenant: {type:String},
      volSize: {type:String},
      boxDisabled: {required:true, type:Boolean},
      status: {required:true, type:Boolean},
      volumes: {type:Object}
    },
    methods: {
      onClick: function() {
        if (this.status == false){
          if (this.boxDisabled == true) {
            if (this.pubkey != '' && this.workers != '' && this.password != '' && this.flavor != '' && this.tenant != '') {

              const requestOptions = { public_key: this.pubkey, workers: this.workers, 
                  password: this.password, flavor: this.flavor, tenant: this.tenant,
                  volume_name: this.volumes[this.tenant], status: this.status };

              axios.post("/cluster-launcher/api/hail/frontend/create", requestOptions)
                .then(response => this.requestOptionsID = response.data.id);

              this.$emit("update-status")
            }
          }
          else if (this.boxDisabled == false) {
            if (this.pubkey != '' && this.volSize != '' && this.workers != '' && this.password != '' && this.flavor != '' && this.tenant != '') {

              const requestOptions = { public_key: this.pubkey, workers: this.workers, 
                  password: this.password, flavor: this.flavor, tenant: this.tenant, 
                  volSize:this.volSize, status: this.status };

              axios.post("/cluster-launcher/api/hail/frontend/create", requestOptions)
                .then(response => this.requestOptionsID = response.data.id);
             
              this.$emit("update-status")
            }
          }
        }
        else if (this.status == true){
          const requestOptions = { status: this.status };
          axios.post("/cluster-launcher/api/hail/frontend/destroy", requestOptions)
            .then(response => this.requestOptionsID = response.data.id);

          this.$emit("update-status")          
        }
      }      
    }
  }
</script>

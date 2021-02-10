<template>
<button @click="onClick" class="DButton">
  <slot>Button</slot>
</button>
</template>

<script>
  import axios from 'axios'
  export default {
    props: {
      pubkey: {required: true, type:String},
      workers: {required: true, type:String},
      password: {required: true, type:String},
      flavor: {required: true, type:String},
      status: {type: Boolean}
    },
    methods: {
      onClick: function() {
        const requestOptions = { public_key: this.pubkey, workers: this.workers, password: this.password, flavor: this.flavor, status: this.status };
        axios.post("/api/hail/frontend/destroy", requestOptions)
          .then(response => this.requestOptionsID = response.data.id);
          
        let newStatus = this.status
        console.log("status = " + newStatus)
        newStatus =! newStatus
        this.$emit("update-status")
        console.log(newStatus)
      }      
    }
  }
</script>

<style>
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

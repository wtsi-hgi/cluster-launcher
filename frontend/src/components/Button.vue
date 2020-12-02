<template>
<button @click="onClick" class="Button">
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
      flavor: {required: true, type:String}      
    },
    methods: {
      onClick: function() {
        if (this.pubkey != '' && this.workers != '' && this.password != '' && this.flavor != '') {
          const requestOptions = { public_key: this.pubkey, workers: this.workers, password: this.password, flavor: this.flavor };
          axios.post("/api/hail/frontend", requestOptions)
            .then(response => this.requestOptionsID = response.data.id);
          console.log(this.workers)
        }
      }
    }
  }
</script>

<style>
.Button{
  font-size:24px;
  color: white;
  margin: 4px 2px;
  text-align: center;
  display: inline-block;
  background-color: #4CAF50;
}
</style>

<template>
  <div id="app">
    <div id='dropdownlist' style="margin:50px auto 0; width:250px;">
      <br>
      <ejs-dropdownlist :dataSource='localData' :fields='localField'
      placeholder='Select A Flavour' popupWidth="250px" popupHeight="200px">
      </ejs-dropdownlist>
    </div>
  </div>
</template>

<script>
import Vue from 'vue';
import { DropDownListPlugin } from '@syncfusion/ej2-vue-dropdowns';
Vue.use(DropDownListPlugin);

export default Vue.extend({
  data: function() {
    return {
      localData:[
        { Id: 'foo1', Flavor: 'bar1' }, 
        { Id: 'foo2', Flavor: 'bar2' },
        { Id: 'foo3', Flavor: 'bar3' }
      ],
      localField: {value: 'Id', text: 'Flavor'}
    };
  },
  mounted(){
    this.getFlavors()
  },

  methods: {
    async getFlavors(){
        const response = await fetch('172.27.17.127:5000/hail' + '/backend')
        console.log(response)
        const wholeResponse = await response.json()
        print(wholeResponse)
    }
  },
})
</script>

<style>
@import url(https://cdn.syncfusion.com/ej2/material.css);
</style>

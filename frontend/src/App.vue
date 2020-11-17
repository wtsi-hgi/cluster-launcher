<template>
  <div id="app">
    <div id='dropdownlist' style="margin:50px auto 0; width:250px;">
      <br>
      <ejs-dropdownlist :dataSource='remoteData' :fields='remoteFields'
      placeholder='Select A Flavour' popupWidth="250px" popupHeight="200px"
      allowFiltering='true'>
      </ejs-dropdownlist>
    </div>
  </div>
</template>

<script>
  import Vue from 'vue';
  import { DropDownListPlugin } from '@syncfusion/ej2-vue-dropdowns';
  import { DataManager, WebApiAdaptor } from '@syncfusion/ej2-data';
  Vue.use(DropDownListPlugin);
  var remoteDataSource = new DataManager({
    url: 'http://172.27.17.127:5000/hail/api/flavors/',
    adaptor: new WebApiAdaptor,
    crossDomain: true
  });
  export default Vue.extend({
    data: function() {
      return {

        remoteData: remoteDataSource,
        remoteFields: { value: 'Id', text: 'Name', groupBy: 'Category' }


/*
        localData:[
          { Id: 'foo1', Flavor: 'bar1' }, 
          { Id: 'foo2', Flavor: 'bar2' },
          { Id: 'foo3', Flavor: 'bar3' }
        ],
        localField: {value: 'Id', text: 'Flavor'}
*/
      };
    },


    mounted(){
      this.getFlavors()
    },

    methods: {
      async getFlavors(){
          const response = await fetch('http://172.27.17.127:5000/hail' + '/api/flavors')
          console.log(response)
      }
    },
  })
</script>

<style>
@import url(https://cdn.syncfusion.com/ej2/material.css);
</style>

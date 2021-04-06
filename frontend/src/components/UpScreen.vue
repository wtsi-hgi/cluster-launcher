<template>
  <div>
    <div class="header">
      <div class="header-text">
        <p>Date/Time: </p>
      </div>
      <d-button :status=this.status v-on="$listeners"> Destroy Cluster </d-button>
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
</template>

<script>
  import Button from './Button.vue'
  export default {
    name: 'App',
    components: {
      'd-button': Button,
    },
    props: {
      status: {type: Boolean},
      ip: {type: String}
    }
  }
</script>

<template>
  <div>
    <select required id="dropDown" @change="onChange()" v-model="output">
      <option>Select Tenant</option>
      <option v-for="choice in choices" :key=choice.id>{{ choice }}</option>
    </select>
  </div>
</template>


<script>
  export default {
    props: {
      choices: {type:Array},
      result: {type:String},
      volumes: {type:Object}
    },
    data: function() {
      return {
        output: ""
      }
    },
    methods: {
      onChange: function() {
        if (this.volumes[this.output] != null) {
          this.$emit("enable-box", this.output)
        }
        else {
          console.log(this.volumes[this.output])
          this.$emit("disable-box", this.output)
        }
      }
    }
  }
</script>

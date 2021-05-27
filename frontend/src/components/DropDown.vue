<template>
  <div>
    <select required id="dropDown" @change="onChange()" v-model="output">
      <option value="" disabled selected hidden> {{ this.display }} </option>
      <option v-for="choice in choices" :key=choice.id>{{ choice }}</option>
    </select>
  </div>
</template>


<script>
  export default {
    props: {
      choices: {type:Array},
      display: {type:String},
      volumes: {type:Object},
      flavourList: {type:Object}
    },
    data: function() {
      return {
        output: ""
      }
    },
    methods: {
      onChange: function() {
        if (this.volumes == null) {
         this.$emit("flavour", this.output)
        }
        else {
          if (this.volumes[this.output] != null) {
            this.$emit("enable-volume-box", this.output)
          }
          else {
            this.$emit("disable-volume-box", this.output)
          }
        }
      }
    }
  }
</script>

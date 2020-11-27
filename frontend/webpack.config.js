module.exports = {
 devServer: {
     proxy: 'https://localhost:5000/hail/frontend'
 } }
{
    resolve: {
        alias: {
            vue: 'vue/dist/vue.js'
        },
    },
}

module.exports = {
  runtimeCompiler: true,
  devServer: {
    proxy: 'https://172.27.17.127:5000/hail/frontend'
  }
}

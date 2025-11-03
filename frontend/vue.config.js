const { defineConfig } = require('@vue/cli-service');
const path = require('path');

module.exports = defineConfig({
  transpileDependencies: true,

  chainWebpack: config => {
    config.plugin('copy').tap(args => {
      if (args[0] && args[0].patterns) {
        args[0].patterns[0].globOptions = {
          ...args[0].patterns[0].globOptions,
          ignore: ['**/index.html']
        };
      }
      return args;
    });

    config.resolve.alias
      .set('@', path.resolve(__dirname, 'src'));
  }
});
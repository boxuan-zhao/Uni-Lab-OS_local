// unilab-config.js – Configuration node storing backend URL
module.exports = function (RED) {
  function UnilabConfigNode(config) {
    RED.nodes.createNode(this, config);
    this.url = config.url || 'http://localhost:3000';
    this.name = config.name || 'UniLab Backend';
  }
  RED.nodes.registerType('unilab-config', UnilabConfigNode);
};

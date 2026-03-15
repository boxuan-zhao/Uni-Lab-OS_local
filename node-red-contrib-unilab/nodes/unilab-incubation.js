// unilab-incubation.js
const makeOperationNode = require('./unilab-operation-base');
module.exports = function (RED) {
  makeOperationNode(RED, 'unilab-incubation', ['duration', 'temperature', 'shaking_speed']);
};

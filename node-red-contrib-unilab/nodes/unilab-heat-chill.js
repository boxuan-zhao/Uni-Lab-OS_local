// unilab-heat-chill.js
const makeOperationNode = require('./unilab-operation-base');
module.exports = function (RED) {
  makeOperationNode(RED, 'unilab-heat-chill', ['target_temp', 'hold_time', 'ramp_rate']);
};

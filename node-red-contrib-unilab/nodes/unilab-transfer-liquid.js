// unilab-transfer-liquid.js
const makeOperationNode = require('./unilab-operation-base');
module.exports = function (RED) {
  makeOperationNode(RED, 'unilab-transfer-liquid', [
    'asp_vol', 'dis_vol', 'sources', 'targets', 'liquid_class', 'mix_cycles'
  ]);
};

// unilab-move-labware.js
const makeOperationNode = require('./unilab-operation-base');
module.exports = function (RED) {
  makeOperationNode(RED, 'unilab-move-labware', ['source', 'target', 'labware_type']);
};

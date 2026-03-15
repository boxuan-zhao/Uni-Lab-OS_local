// unilab-device-list.js – Fetch online devices from backend
module.exports = function (RED) {
  function DeviceListNode(config) {
    RED.nodes.createNode(this, config);
    const node = this;
    const backendCfg = RED.nodes.getNode(config.backend);

    node.on('input', async function (msg) {
      if (!backendCfg) { node.error('No backend config', msg); return; }
      try {
        const res = await fetch(`${backendCfg.url}/api/devices`);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        msg.payload = await res.json();
        node.send(msg);
      } catch (err) {
        node.error(err.message, msg);
      }
    });
  }
  RED.nodes.registerType('unilab-device-list', DeviceListNode);
};

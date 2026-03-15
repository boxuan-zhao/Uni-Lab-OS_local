// unilab-device-monitor.js – WebSocket listener that pushes device status downstream
module.exports = function (RED) {
  function DeviceMonitorNode(config) {
    RED.nodes.createNode(this, config);
    const node = this;
    const backendCfg = RED.nodes.getNode(config.backend);

    let ws = null;
    let reconnectTimer = null;

    function connect() {
      if (!backendCfg) { node.error('No backend config'); return; }
      const wsUrl = backendCfg.url.replace(/^http/, 'ws') + '/ws/device-status';
      node.status({ fill: 'yellow', shape: 'ring', text: '连接中...' });

      try {
        const WebSocket = require('ws');
        ws = new WebSocket(wsUrl);

        ws.on('open', () => {
          node.status({ fill: 'green', shape: 'dot', text: '已连接' });
        });

        ws.on('message', (data) => {
          try {
            const payload = JSON.parse(data.toString());
            node.send({ payload, topic: 'device-status' });
          } catch (e) {
            node.send({ payload: data.toString(), topic: 'device-status' });
          }
        });

        ws.on('error', (err) => {
          node.status({ fill: 'red', shape: 'ring', text: err.message });
        });

        ws.on('close', () => {
          node.status({ fill: 'red', shape: 'ring', text: '已断开，重连中...' });
          reconnectTimer = setTimeout(connect, 5000);
        });
      } catch (err) {
        node.error(`WebSocket error: ${err.message}`);
        reconnectTimer = setTimeout(connect, 5000);
      }
    }

    connect();

    node.on('close', function (done) {
      clearTimeout(reconnectTimer);
      if (ws) { ws.terminate(); ws = null; }
      done();
    });
  }
  RED.nodes.registerType('unilab-device-monitor', DeviceMonitorNode);
};

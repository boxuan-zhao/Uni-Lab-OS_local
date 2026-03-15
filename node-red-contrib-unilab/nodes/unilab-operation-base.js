/**
 * Shared helper to create UniLab operation nodes.
 * Each operation node represents one step in a protocol flow.
 * It does NOT call UniLab directly—it is converted by the backend converter.
 * To execute immediately as a single job, trigger via unilab-submit-job or use
 * msg.payload passthrough.
 *
 * @param {object} RED   Node-RED runtime
 * @param {string} type  Node type string (e.g. 'unilab-transfer-liquid')
 * @param {string[]} paramKeys  Keys to collect from config as action_args
 */
function makeOperationNode(RED, type, paramKeys) {
  function OperationNode(config) {
    RED.nodes.createNode(this, config);
    const node = this;
    const backendCfg = RED.nodes.getNode(config.backend);

    node.on('input', async function (msg) {
      // Build action_args from config + any msg overrides
      const action_args = {};
      for (const k of paramKeys) {
        action_args[k] = msg[k] !== undefined ? msg[k] : config[k];
      }

      const nodeType = type;
      const ACTION_MAP = {
        'unilab-transfer-liquid': 'transfer_liquid',
        'unilab-incubation':      'incubation',
        'unilab-heat-chill':      'heat_chill',
        'unilab-move-labware':    'move_labware',
      };
      const action = ACTION_MAP[nodeType] || nodeType;

      // Mode A: just pass along the job descriptor (used in protocol flows)
      if (config.mode === 'descriptor') {
        msg.payload = {
          type: nodeType,
          device_id: config.device_id || msg.device_id || '',
          action,
          action_args,
        };
        node.send(msg);
        return;
      }

      // Mode B: execute immediately via backend single-job API
      if (!backendCfg) { node.error('No backend config', msg); return; }
      node.status({ fill: 'blue', shape: 'dot', text: '执行中...' });
      try {
        const res = await fetch(`${backendCfg.url}/api/jobs/submit-single`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            device_id: config.device_id || msg.device_id || '',
            action,
            action_args,
          }),
        });
        if (!res.ok) {
          const err = await res.json().catch(() => ({ detail: res.statusText }));
          throw new Error(err.detail || res.statusText);
        }
        const data = await res.json();
        node.status({ fill: 'green', shape: 'dot', text: '已提交' });
        msg.payload = data;
        msg.jobId = data.id;
        node.send(msg);
      } catch (err) {
        node.status({ fill: 'red', shape: 'ring', text: err.message });
        node.error(err.message, msg);
      }
    });
  }
  RED.nodes.registerType(type, OperationNode);
}

module.exports = makeOperationNode;

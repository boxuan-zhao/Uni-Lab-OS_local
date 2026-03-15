// unilab-submit-job.js – Submit a protocol as a sequence of UniLab jobs
module.exports = function (RED) {
  function SubmitJobNode(config) {
    RED.nodes.createNode(this, config);
    const node = this;
    const backendCfg = RED.nodes.getNode(config.backend);

    node.on('input', async function (msg) {
      if (!backendCfg) { node.error('No backend config', msg); return; }
      const protocolId = msg.protocolId || config.protocolId;
      if (!protocolId) { node.error('No protocol_id provided', msg); return; }

      node.status({ fill: 'blue', shape: 'dot', text: '提交中...' });
      try {
        const res = await fetch(`${backendCfg.url}/api/jobs/submit`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ protocol_id: protocolId })
        });
        if (!res.ok) {
          const err = await res.json().catch(() => ({ detail: res.statusText }));
          throw new Error(err.detail || res.statusText);
        }
        const data = await res.json();
        msg.payload = data;
        msg.jobIds = (data.jobs || []).map(j => j.id);
        node.status({ fill: 'green', shape: 'dot', text: `已提交 ${msg.jobIds.length} 个任务` });
        node.send(msg);
      } catch (err) {
        node.status({ fill: 'red', shape: 'ring', text: err.message });
        node.error(err.message, msg);
      }
    });
  }
  RED.nodes.registerType('unilab-submit-job', SubmitJobNode);
};

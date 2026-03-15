// unilab-job-status.js – Poll job status until terminal state
module.exports = function (RED) {
  function JobStatusNode(config) {
    RED.nodes.createNode(this, config);
    const node = this;
    const backendCfg = RED.nodes.getNode(config.backend);
    const pollInterval = (Number(config.pollInterval) || 5) * 1000;

    // Status codes: 1=submitted 2=running 4=success 5=cancelled 6=aborted
    const TERMINAL = new Set([4, 5, 6]);

    async function pollJob(jobId, msg) {
      if (!backendCfg) { node.error('No backend config', msg); return; }
      node.status({ fill: 'blue', shape: 'dot', text: `轮询 ${jobId}` });

      const poll = setInterval(async () => {
        try {
          const res = await fetch(`${backendCfg.url}/api/jobs/${jobId}/status`);
          if (!res.ok) throw new Error(`HTTP ${res.status}`);
          const data = await res.json();
          const status = data.status;

          if (TERMINAL.has(status)) {
            clearInterval(poll);
            const isSuccess = status === 4;
            node.status({
              fill: isSuccess ? 'green' : 'red',
              shape: 'dot',
              text: isSuccess ? '成功' : `状态 ${status}`
            });
            const outMsg = { ...msg, payload: data, jobStatus: status };
            // output[0] = success, output[1] = failure
            node.send(isSuccess ? [outMsg, null] : [null, outMsg]);
          } else {
            node.status({ fill: 'yellow', shape: 'dot', text: `执行中 (${status})` });
          }
        } catch (err) {
          node.warn(`轮询错误: ${err.message}`);
        }
      }, pollInterval);
    }

    node.on('input', function (msg) {
      const jobId = msg.jobId || config.jobId;
      if (!jobId) {
        // If jobIds array provided, poll all of them
        if (Array.isArray(msg.jobIds)) {
          msg.jobIds.forEach(id => pollJob(id, { ...msg, jobId: id }));
        } else {
          node.error('No job ID provided', msg);
        }
        return;
      }
      pollJob(jobId, msg);
    });
  }
  RED.nodes.registerType('unilab-job-status', JobStatusNode);
};

// Logging for core events
function logEvent(type, agent, detail) {
  console.log(JSON.stringify({ type, agent, detail, timestamp: Date.now() }));
}

// Entropy calculation and role mutation trigger
function checkEntropyAndTriggerMutation(entropy, agents) {
  if (entropy > 0.9 && Math.random() < 0.25) {
    const agent = agents[Math.floor(Math.random() * agents.length)];
    mutateRole(agent);
    logEvent("role_mutation", agent.name, agent.role);
  }
}

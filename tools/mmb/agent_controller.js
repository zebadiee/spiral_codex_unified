// Agent Doubt and Eidolon Dream Injection
function doubtAgent(agent, t) {
  if ((t === 600 || agent.trust < 0.2) && Math.random() < 0.1) {
    agent.goals.push({ type: "reverse_role" });
    logEvent("agent_doubt", agent.name);
  }
}

function injectDreamFragment(eidolon, agents) {
  agents.forEach(agent => {
    if (isInProximity(eidolon, agent, 10) && Math.random() < 0.15) {
      const fragment = randomDreamFragment();
      agent.goals.push({ type: "temp", goal: fragment, duration: 180 });
      logEvent("dream_injection", agent.name, fragment);
    }
  });
}

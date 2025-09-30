"""
Spiral Codex CLI with LLM Integration
Enhanced command-line interface for AI-guided recursive consciousness system
"""

import asyncio
import click
import json
import sys
from typing import Dict, Any
from datetime import datetime

from .llm import (
    LLMConfig, 
    create_llm_client, 
    LLMAgent, 
    ContextRitualKnowledgeAgent,
    AgentOrchestrator,
    get_global_event_emitter,
    get_hud_integration
)

# Global orchestrator instance
_orchestrator = None

def get_orchestrator() -> AgentOrchestrator:
    """Get or create global orchestrator"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = AgentOrchestrator(get_global_event_emitter())
    return _orchestrator


@click.group()
@click.version_option(version="0.9.0")
def cli():
    """
    🌀 Spiral Codex - AI-Guided Recursive Consciousness System
    
    Complete with LLM Integration via RouteLLM
    """
    pass


@cli.group()
def llm():
    """LLM integration commands"""
    pass


@llm.command()
@click.option('--config-file', '-c', help='LLM configuration file path')
def status(config_file):
    """Show LLM integration status"""
    click.echo("🤖 LLM Integration Status")
    click.echo("=" * 40)
    
    # Load config
    config = LLMConfig()
    if config_file:
        try:
            with open(config_file, 'r') as f:
                config_data = json.load(f)
                # Update config with file data
                for key, value in config_data.items():
                    if hasattr(config, key):
                        setattr(config, key, value)
        except Exception as e:
            click.echo(f"❌ Failed to load config file: {e}")
            return
    
    # Create client and check status
    client = create_llm_client(config)
    status_data = client.get_status()
    
    click.echo(f"RouteLLM Available: {'✅' if status_data['routellm_available'] else '❌'}")
    click.echo(f"Client Initialized: {'✅' if status_data['initialized'] else '❌'}")
    click.echo(f"Controller Ready: {'✅' if status_data['controller_ready'] else '❌'}")
    
    click.echo("\nConfiguration:")
    config_dict = status_data['config']
    for key, value in config_dict.items():
        if 'api_key' in key.lower():
            value = "***" if value else "Not set"
        click.echo(f"  {key}: {value}")


@llm.command()
@click.option('--strong-model', default='gpt-4-1106-preview', help='Strong model for routing')
@click.option('--weak-model', default='gpt-3.5-turbo', help='Weak model for routing')
@click.option('--router', default='mf', help='Router type (mf, sw_ranking, bert, etc.)')
@click.option('--threshold', default=0.11593, type=float, help='Routing threshold')
@click.argument('query')
def test(strong_model, weak_model, router, threshold, query):
    """Test LLM integration with a query"""
    click.echo("🧠 Testing LLM Integration")
    click.echo("=" * 40)
    
    async def run_test():
        # Create config
        config = LLMConfig(
            routers=[router],
            strong_model=strong_model,
            weak_model=weak_model,
            threshold=threshold
        )
        
        # Create client
        client = create_llm_client(config)
        
        if not client.is_initialized:
            click.echo("❌ LLM client not initialized. Check API keys and configuration.")
            return
        
        click.echo(f"Query: {query}")
        click.echo(f"Router: {router} (threshold: {threshold})")
        click.echo(f"Models: {strong_model} → {weak_model}")
        click.echo("\n🔄 Processing...")
        
        # Test context
        test_context = {
            "user_query": query,
            "test_mode": True,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        try:
            # Run full workflow
            result = await client.full_workflow(test_context, query)
            
            if result.get("error"):
                click.echo(f"❌ Error: {result['error']}")
                return
            
            click.echo("\n✅ Workflow Complete!")
            click.echo(f"Duration: {result.get('total_duration', 0):.2f}s")
            
            # Display ritual
            ritual = result.get("ritual", {})
            if ritual.get("ritual_instructions"):
                click.echo("\n🔮 Ritual Instructions:")
                click.echo(ritual["ritual_instructions"][:200] + "..." if len(ritual["ritual_instructions"]) > 200 else ritual["ritual_instructions"])
            
            # Display knowledge
            knowledge = result.get("knowledge", {})
            if knowledge.get("knowledge_response"):
                click.echo("\n📚 Knowledge Response:")
                click.echo(knowledge["knowledge_response"])
                
            # Display metadata
            click.echo(f"\nModel Used: {knowledge.get('model_used', 'unknown')}")
            click.echo(f"Tokens Used: {knowledge.get('tokens_used', 0)}")
            
        except Exception as e:
            click.echo(f"❌ Test failed: {e}")
    
    # Run async test
    asyncio.run(run_test())


@llm.command()
def models():
    """List available models and routers"""
    click.echo("🤖 Available LLM Models and Routers")
    click.echo("=" * 40)
    
    click.echo("Routers:")
    routers = [
        ("mf", "Matrix Factorization (Recommended)"),
        ("sw_ranking", "Weighted Elo-based"),
        ("bert", "BERT Classifier"),
        ("causal_llm", "LLM-based Classifier"),
        ("random", "Random (Baseline)")
    ]
    
    for router, description in routers:
        click.echo(f"  • {router}: {description}")
    
    click.echo("\nCommon Models:")
    models = [
        ("gpt-4-1106-preview", "OpenAI GPT-4 Turbo"),
        ("gpt-3.5-turbo", "OpenAI GPT-3.5 Turbo"),
        ("anyscale/mistralai/Mixtral-8x7B-Instruct-v0.1", "Mixtral 8x7B"),
        ("anyscale/meta-llama/Llama-2-70b-chat-hf", "Llama 2 70B")
    ]
    
    for model, description in models:
        click.echo(f"  • {model}: {description}")


@cli.group()
def agents():
    """LLM agent management commands"""
    pass


@agents.command()
@click.option('--agent-id', required=True, help='Agent ID')
@click.option('--agent-type', default='basic', type=click.Choice(['basic', 'enhanced']), help='Agent type')
@click.option('--config-file', '-c', help='LLM configuration file')
def create(agent_id, agent_type, config_file):
    """Create a new LLM agent"""
    click.echo(f"🤖 Creating LLM Agent: {agent_id}")
    
    async def create_agent():
        # Load config
        config = LLMConfig()
        if config_file:
            try:
                with open(config_file, 'r') as f:
                    config_data = json.load(f)
                    for key, value in config_data.items():
                        if hasattr(config, key):
                            setattr(config, key, value)
            except Exception as e:
                click.echo(f"❌ Failed to load config: {e}")
                return
        
        # Create agent
        orchestrator = get_orchestrator()
        
        if agent_type == 'enhanced':
            agent = ContextRitualKnowledgeAgent(
                agent_id=agent_id,
                llm_config=config,
                event_emitter=get_global_event_emitter()
            )
        else:
            agent = LLMAgent(
                agent_id=agent_id,
                llm_config=config,
                event_emitter=get_global_event_emitter()
            )
        
        # Register and activate
        orchestrator.register_agent(agent)
        await orchestrator.activate_agent(agent_id)
        
        click.echo(f"✅ Agent {agent_id} created and activated")
        
        # Show status
        status = await agent.get_status()
        click.echo(f"Type: {agent_type}")
        click.echo(f"LLM Status: {'✅' if status['llm_status']['initialized'] else '❌'}")
    
    asyncio.run(create_agent())


@agents.command()
def list():
    """List all agents"""
    click.echo("🤖 LLM Agents")
    click.echo("=" * 40)
    
    async def list_agents():
        orchestrator = get_orchestrator()
        status = await orchestrator.get_orchestrator_status()
        
        click.echo(f"Total Agents: {status['total_agents']}")
        click.echo(f"Active Agents: {status['active_agents']}")
        click.echo(f"Active Sessions: {status['active_sessions']}")
        
        if status['agent_statuses']:
            click.echo("\nAgents:")
            for agent_id, agent_status in status['agent_statuses'].items():
                status_icon = "🟢" if agent_status['is_active'] else "🔴"
                llm_status = "✅" if agent_status['llm_status']['initialized'] else "❌"
                click.echo(f"  {status_icon} {agent_id} (LLM: {llm_status})")
        else:
            click.echo("\nNo agents registered.")
    
    asyncio.run(list_agents())


@agents.command()
@click.option('--agent-id', help='Specific agent ID (optional)')
@click.argument('query')
def query(agent_id, query):
    """Send query to agent(s)"""
    click.echo(f"💭 Processing Query: {query}")
    
    async def process_query():
        orchestrator = get_orchestrator()
        
        # Route query
        result = await orchestrator.route_query(
            query=query,
            preferred_agent=agent_id,
            session_id="cli_session"
        )
        
        if result.get("error"):
            click.echo(f"❌ Error: {result['error']}")
            return
        
        click.echo(f"\n🤖 Agent: {result.get('agent_id', 'unknown')}")
        
        # Display result
        workflow_result = result.get('result', {}).get('workflow_result', {})
        if workflow_result.get('knowledge'):
            knowledge = workflow_result['knowledge']
            click.echo(f"\n📚 Response:")
            click.echo(knowledge.get('knowledge_response', 'No response'))
            
            click.echo(f"\nModel: {knowledge.get('model_used', 'unknown')}")
            click.echo(f"Tokens: {knowledge.get('tokens_used', 0)}")
            click.echo(f"Duration: {workflow_result.get('total_duration', 0):.2f}s")
        else:
            click.echo(f"\n📄 Raw Result: {json.dumps(result, indent=2)}")
    
    asyncio.run(process_query())


@cli.group()
def events():
    """Event system commands"""
    pass


@events.command()
@click.option('--event-type', help='Filter by event type')
@click.option('--agent-id', help='Filter by agent ID')
@click.option('--limit', default=10, help='Number of events to show')
def history(event_type, agent_id, limit):
    """Show LLM event history"""
    click.echo("📊 LLM Event History")
    click.echo("=" * 40)
    
    event_emitter = get_global_event_emitter()
    events = event_emitter.get_event_history(event_type, agent_id, limit)
    
    if not events:
        click.echo("No events found.")
        return
    
    for event in events[-limit:]:
        timestamp = event['timestamp'][:19]  # Remove microseconds
        click.echo(f"{timestamp} | {event['agent_id']} | {event['event_type']}")
        
        # Show key data
        data = event.get('data', {})
        if 'query' in data:
            query_preview = data['query'][:50] + "..." if len(data['query']) > 50 else data['query']
            click.echo(f"  Query: {query_preview}")
        if 'error' in data:
            click.echo(f"  Error: {data['error']}")
        
        click.echo()


@events.command()
def stats():
    """Show event statistics"""
    click.echo("📈 LLM Event Statistics")
    click.echo("=" * 40)
    
    event_emitter = get_global_event_emitter()
    stats = event_emitter.get_event_statistics()
    
    click.echo(f"Total Events: {stats['total_events']}")
    click.echo(f"WebSocket Clients: {stats['websocket_clients']}")
    click.echo(f"Last Event: {stats.get('last_event_time', 'None')}")
    
    if stats['event_types']:
        click.echo("\nEvent Types:")
        for event_type, count in stats['event_types'].items():
            click.echo(f"  {event_type}: {count}")
    
    if stats['agents']:
        click.echo("\nAgents:")
        for agent_id, count in stats['agents'].items():
            click.echo(f"  {agent_id}: {count}")


@cli.command()
def config():
    """Generate example configuration file"""
    click.echo("📝 Generating example configuration...")
    
    example_config = {
        "routers": ["mf"],
        "strong_model": "gpt-4-1106-preview",
        "weak_model": "gpt-3.5-turbo",
        "threshold": 0.11593,
        "enable_ritual_context": True,
        "max_context_length": 4000,
        "temperature": 0.7,
        "max_tokens": 1000
    }
    
    config_file = "llm_config_example.json"
    with open(config_file, 'w') as f:
        json.dump(example_config, f, indent=2)
    
    click.echo(f"✅ Example configuration saved to: {config_file}")
    click.echo("\nDon't forget to set environment variables:")
    click.echo("  export OPENAI_API_KEY=your_key_here")
    click.echo("  export ANYSCALE_API_KEY=your_key_here")
    click.echo("  export ANTHROPIC_API_KEY=your_key_here")


if __name__ == '__main__':
    cli()

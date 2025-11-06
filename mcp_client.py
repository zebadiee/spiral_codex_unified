# mcp_client.py
"""
Spiral Codex Unified - MCP Client
Auto-discovers and calls MCP tools across the agent federation
"""
import os
import yaml
import requests
import json
from typing import Dict, List, Any
from datetime import datetime

CFG = os.getenv("MCP_CONFIG", os.path.expanduser("~/.config/mcp/servers.yaml"))

def load_servers() -> List[Dict]:
    """Load MCP server configuration"""
    try:
        with open(CFG) as f:
            config = yaml.safe_load(f)
        return config.get("servers", [])
    except FileNotFoundError:
        print(f"⚠️  MCP config not found at {CFG}")
        return []
    except Exception as e:
        print(f"❌ Error loading MCP config: {e}")
        return []

def discover_tools() -> Dict[str, Dict]:
    """Auto-discover all available tools from all MCP servers"""
    tools = {}
    servers = load_servers()

    print(f"🔍 Discovering tools from {len(servers)} servers...")

    for server in servers:
        server_id = server.get('id', 'unknown')
        server_url = server.get('url', '')

        if not server_url:
            print(f"⚠️  Server {server_id} has no URL configured")
            continue

        try:
            response = requests.get(f"{server_url}/tools/list", timeout=5)
            if response.status_code == 200:
                server_tools = response.json().get("tools", [])
                for tool in server_tools:
                    tool_name = tool.get("name", "")
                    if tool_name:
                        full_key = f"{server_id}.{tool_name}"
                        tools[full_key] = {
                            "server": server,
                            "tool": tool,
                            "url": server_url
                        }
                print(f"✅ {server_id}: {len(server_tools)} tools discovered")
            else:
                print(f"❌ {server_id}: HTTP {response.status_code}")

        except requests.exceptions.Timeout:
            print(f"⏰ {server_id}: Timeout")
        except requests.exceptions.ConnectionError:
            print(f"🔌 {server_id}: Connection refused")
        except Exception as e:
            print(f"❌ {server_id}: {str(e)}")

    print(f"🎯 Total tools discovered: {len(tools)}")
    return tools

def call(tool_key: str, args: Dict = None) -> Dict[str, Any]:
    """Call a specific tool by key (server.tool_name)"""
    if args is None:
        args = {}

    if '.' not in tool_key:
        return {"error": f"Invalid tool key format: {tool_key}. Use 'server.tool_name'"}

    server_id, tool_name = tool_key.split('.', 1)
    servers = {s['id']: s for s in load_servers()}

    if server_id not in servers:
        return {"error": f"Unknown server: {server_id}"}

    server = servers[server_id]
    url = server.get('url', '')

    if not url:
        return {"error": f"Server {server_id} has no URL configured"}

    try:
        payload = {
            "name": tool_name,
            "arguments": args
        }

        response = requests.post(
            f"{url}/tools/call",
            json=payload,
            timeout=30,
            headers={'Content-Type': 'application/json'}
        )

        if response.status_code == 200:
            result = response.json()
            # Add metadata
            result['_metadata'] = {
                'tool_key': tool_key,
                'server_id': server_id,
                'tool_name': tool_name,
                'timestamp': datetime.utcnow().isoformat()
            }
            return result
        else:
            return {
                "error": f"HTTP {response.status_code}: {response.text}",
                "tool_key": tool_key,
                "server_id": server_id
            }

    except requests.exceptions.Timeout:
        return {"error": f"Timeout calling {tool_key}", "tool_key": tool_key}
    except requests.exceptions.ConnectionError:
        return {"error": f"Connection refused for {tool_key}", "tool_key": tool_key}
    except Exception as e:
        return {"error": f"Failed to call {tool_key}: {str(e)}", "tool_key": tool_key}

def list_tools() -> None:
    """List all discovered tools in a readable format"""
    tools = discover_tools()

    if not tools:
        print("❌ No tools discovered")
        return

    print(f"\n🧠 Available MCP Tools ({len(tools)} total):\n")

    # Group by server
    by_server = {}
    for key, tool_info in tools.items():
        server_id = tool_info['server']['id']
        if server_id not in by_server:
            by_server[server_id] = []
        by_server[server_id].append((key, tool_info))

    for server_id, server_tools in by_server.items():
        server_url = server_tools[0][1]['server']['url']
        print(f"📡 {server_id} ({server_url})")
        for tool_key, tool_info in server_tools:
            tool = tool_info['tool']
            description = tool.get('description', 'No description')
            print(f"   🔧 {tool_key}: {description}")
        print()

def health_check() -> Dict[str, Any]:
    """Check health of all MCP servers"""
    servers = load_servers()
    results = {}

    for server in servers:
        server_id = server.get('id', 'unknown')
        server_url = server.get('url', '')

        try:
            response = requests.get(f"{server_url}/tools/list", timeout=3)
            if response.status_code == 200:
                tools_count = len(response.json().get("tools", []))
                results[server_id] = {
                    "status": "healthy",
                    "url": server_url,
                    "tools_count": tools_count,
                    "response_time": response.elapsed.total_seconds()
                }
            else:
                results[server_id] = {
                    "status": "error",
                    "url": server_url,
                    "error": f"HTTP {response.status_code}"
                }
        except Exception as e:
            results[server_id] = {
                "status": "unreachable",
                "url": server_url,
                "error": str(e)
            }

    return results

# CLI functionality
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python mcp_client.py [list|health|call tool.name '{args}']")
        sys.exit(1)

    command = sys.argv[1]

    if command == "list":
        list_tools()
    elif command == "health":
        health = health_check()
        print("🏥 MCP Server Health:\n")
        for server_id, info in health.items():
            status = info['status']
            icon = "✅" if status == "healthy" else "❌"
            print(f"{icon} {server_id}: {status}")
            if status == "healthy":
                print(f"   📊 Tools: {info['tools_count']}, ⏱️  Response: {info['response_time']:.3f}s")
            else:
                print(f"   ❌ {info.get('error', 'Unknown error')}")
    elif command == "call" and len(sys.argv) >= 3:
        tool_key = sys.argv[2]
        args = {}
        if len(sys.argv) >= 4:
            try:
                args = json.loads(sys.argv[3])
            except json.JSONDecodeError:
                print("❌ Invalid JSON arguments")
                sys.exit(1)

        result = call(tool_key, args)
        print(f"🔧 Calling {tool_key}:")
        print(json.dumps(result, indent=2))
    else:
        print("❌ Invalid command")
        sys.exit(1)
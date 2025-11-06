#!/usr/bin/env python3
"""
Test LocalLLMBridge integration with Ollama
"""
import asyncio
import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))

from kernel.local_llm_bridge import create_llm_bridge, AgentLLMWrapper

async def test_ollama_bridge():
    """Test Ollama bridge functionality"""
    print("🧪 Testing LocalLLMBridge with Ollama...")

    try:
        # Create bridge with llama3.1:8b (or mistral)
        bridge = await create_llm_bridge(provider="ollama", model="llama3.1:8b")

        async with bridge:
            # Test connection
            status = bridge.get_status()
            print(f"✅ Bridge status: {status['status']}")

            # Test available models
            models = await bridge.get_available_models()
            print(f"✅ Available models: {models}")

            # Test generation
            print("🔄 Testing text generation...")
            response = await bridge.generate("Hello, this is a test of the Spiral Codex system.")
            print(f"✅ Generation response: {response[:100]}...")

            # Test agent wrapper
            print("🔄 Testing agent wrapper for ƒCODEX...")
            codex_wrapper = AgentLLMWrapper(bridge, "ƒCODEX")
            codex_response = await codex_wrapper.generate_response(
                "Write a simple Python function to add two numbers."
            )
            print(f"✅ Codex response: {codex_response[:100]}...")

            # Test chat
            print("🔄 Testing chat functionality...")
            messages = [
                {"role": "user", "content": "What is Spiral Codex?"},
                {"role": "assistant", "content": "Spiral Codex is a multi-agent system."},
                {"role": "user", "content": "What agents are available?"}
            ]
            chat_response = await bridge.chat(messages)
            print(f"✅ Chat response: {chat_response[:100]}...")

            print("🎉 LocalLLMBridge test completed successfully!")
            return True

    except Exception as e:
        print(f"❌ LocalLLMBridge test failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_ollama_bridge())
    sys.exit(0 if success else 1)
"""
Test patterns for LiveKit Agents demonstrating various testing approaches.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from typing import Any

from livekit.agents import Agent, AgentSession, RunContext
from livekit.agents.testing import mock_tools
from livekit.plugins import openai

# Import your agents (adjust path as needed)
from examples.basic_voice_agent.agent import MyAgent
from examples.tool_enabled_agent.agent import ToolEnabledAgent


class TestBasicAgent:
    """Test cases for basic voice agent."""
    
    @pytest.mark.asyncio
    async def test_agent_initialization(self):
        """Test that agent initializes with correct instructions."""
        agent = MyAgent()
        assert "Kelly" in agent.instructions
        assert "helpful voice assistant" in agent.instructions
    
    @pytest.mark.asyncio
    async def test_agent_greeting(self):
        """Test agent greeting behavior using LLM judge."""
        async with (
            openai.LLM(model="gpt-4o-mini") as llm,
            AgentSession(llm=llm) as session,
        ):
            await session.start(MyAgent())
            
            # Simulate agent entering session
            result = await session.run(user_input=None)
            
            # Validate greeting intent
            await result.expect.next_event().is_message(
                role="assistant"
            ).judge(
                llm,
                intent="Greet the user warmly and introduce yourself as Kelly"
            )
    
    @pytest.mark.asyncio
    async def test_weather_tool_call(self):
        """Test weather lookup function tool."""
        async with (
            openai.LLM(model="gpt-4o-mini") as llm,
            AgentSession(llm=llm) as session,
        ):
            await session.start(MyAgent())
            
            result = await session.run(
                user_input="What's the weather in San Francisco?"
            )
            
            # Expect function call
            result.expect.next_event().is_function_call(
                name="lookup_weather",
                arguments={"location": "San Francisco"}
            )
            
            # Expect function output
            result.expect.next_event().is_function_call_output(
                output__contains="72 degrees"
            )
            
            # Expect agent response about weather
            await result.expect.next_event().is_message(
                role="assistant"
            ).judge(
                llm,
                intent="Inform user about San Francisco weather being 72 degrees and sunny"
            )
    
    @pytest.mark.asyncio
    async def test_weather_tool_mock(self):
        """Test weather tool with mocked response."""
        with mock_tools(
            MyAgent,
            {"lookup_weather": lambda **kwargs: "It's raining cats and dogs!"}
        ):
            async with (
                openai.LLM(model="gpt-4o-mini") as llm,
                AgentSession(llm=llm) as session,
            ):
                await session.start(MyAgent())
                
                result = await session.run(
                    user_input="How's the weather?"
                )
                
                # Function should return mocked response
                result.expect.next_event().is_function_call_output(
                    output="It's raining cats and dogs!"
                )
                
                # Agent should incorporate mocked response
                await result.expect.next_event().is_message(
                    role="assistant"
                ).judge(
                    llm,
                    intent="Tell user it's raining cats and dogs"
                )
    
    @pytest.mark.asyncio
    async def test_multiple_turns(self):
        """Test multi-turn conversation."""
        async with (
            openai.LLM(model="gpt-4o-mini") as llm,
            AgentSession(llm=llm) as session,
        ):
            await session.start(MyAgent())
            
            # First turn - greeting
            result1 = await session.run(user_input="Hello")
            await result1.expect.next_event().is_message(
                role="assistant"
            ).judge(llm, intent="Friendly greeting")
            
            # Second turn - weather question
            result2 = await session.run(
                user_input="What's the weather in Tokyo?"
            )
            result2.expect.contains_function_call(name="lookup_weather")
            
            # Third turn - follow-up
            result3 = await session.run(
                user_input="Is that good weather for sightseeing?"
            )
            await result3.expect.next_event().is_message(
                role="assistant"
            ).judge(
                llm,
                intent="Provide advice about sightseeing based on the weather"
            )


class TestToolEnabledAgent:
    """Test cases for tool-enabled agent."""
    
    @pytest.mark.asyncio
    async def test_multiple_tools_available(self):
        """Test that agent has access to multiple tools."""
        agent = ToolEnabledAgent()
        
        # Get available tools from agent
        tools = agent.get_tools()
        tool_names = [tool.name for tool in tools]
        
        assert "web_search" in tool_names
        assert "calculate" in tool_names
        assert "get_weather" in tool_names
        assert "send_email_draft" in tool_names
    
    @pytest.mark.asyncio
    async def test_calculation_tool(self):
        """Test calculation tool with valid expressions."""
        agent = ToolEnabledAgent()
        context = Mock(spec=RunContext)
        
        # Test valid calculation
        result = await agent.calculate(context, "2 + 2 * 3")
        assert "8" in result
        
        # Test with functions
        result = await agent.calculate(context, "max(5, 10, 3)")
        assert "10" in result
    
    @pytest.mark.asyncio
    async def test_calculation_tool_error(self):
        """Test calculation tool with invalid expressions."""
        agent = ToolEnabledAgent()
        context = Mock(spec=RunContext)
        
        # Test dangerous expression
        with pytest.raises(ToolError):
            await agent.calculate(context, "__import__('os').system('ls')")
        
        # Test invalid syntax
        with pytest.raises(ToolError):
            await agent.calculate(context, "2 ++ 2")
    
    @pytest.mark.asyncio
    async def test_tool_error_handling(self):
        """Test that tool errors are handled gracefully."""
        async with (
            openai.LLM(model="gpt-4o-mini") as llm,
            AgentSession(llm=llm) as session,
        ):
            # Mock web_search to raise error
            with mock_tools(
                ToolEnabledAgent,
                {"web_search": lambda **kwargs: ToolError("Service unavailable")}
            ):
                await session.start(ToolEnabledAgent())
                
                result = await session.run(
                    user_input="Search for LiveKit documentation"
                )
                
                # Agent should handle error gracefully
                await result.expect.next_event().is_message(
                    role="assistant"
                ).judge(
                    llm,
                    intent="Inform user that web search is currently unavailable"
                )


class TestAgentSession:
    """Test AgentSession configuration and behavior."""
    
    @pytest.mark.asyncio
    async def test_session_configuration(self):
        """Test various session configurations."""
        # Test with different turn detection
        session1 = AgentSession(
            llm=openai.LLM(model="gpt-4o-mini"),
            turn_detection="vad",
            allow_interruptions=True,
            min_interruption_duration=0.5,
        )
        assert session1.allow_interruptions == True
        assert session1.min_interruption_duration == 0.5
        
        # Test with manual turn detection
        session2 = AgentSession(
            llm=openai.LLM(model="gpt-4o-mini"),
            turn_detection="manual",
            allow_interruptions=False,
        )
        assert session2.turn_detection == "manual"
        assert session2.allow_interruptions == False
    
    @pytest.mark.asyncio
    async def test_session_events(self):
        """Test session event handling."""
        events_fired = []
        
        async with (
            openai.LLM(model="gpt-4o-mini") as llm,
            AgentSession(llm=llm) as session,
        ):
            @session.on("user_state_changed")
            def on_user_state(ev):
                events_fired.append(("user_state", ev.new_state))
            
            @session.on("agent_state_changed")
            def on_agent_state(ev):
                events_fired.append(("agent_state", ev.new_state))
            
            await session.start(MyAgent())
            
            # Simulate some events
            await session.run(user_input="Hello")
            
            # Check that events were fired
            assert len(events_fired) > 0
            assert any(event[0] == "agent_state" for event in events_fired)


class TestMultiAgentHandoff:
    """Test multi-agent handoff patterns."""
    
    @pytest.mark.asyncio
    async def test_agent_handoff(self):
        """Test agent handoff via tool return."""
        from examples.multi_agent_system.agents import IntakeAgent, BillingAgent
        
        async with (
            openai.LLM(model="gpt-4o-mini") as llm,
            AgentSession(llm=llm) as session,
        ):
            await session.start(IntakeAgent())
            
            # Simulate customer with billing issue
            result = await session.run(
                user_input="I have a problem with my bill"
            )
            
            # Should collect info and route to billing
            result.expect.contains_function_call(
                name="collect_customer_info"
            )
            
            # Should handoff to billing agent
            result.expect.contains_agent_handoff(
                new_agent_type=BillingAgent
            )


# Helper functions for testing

async def create_test_session(**kwargs) -> AgentSession:
    """Create a test session with default configuration."""
    defaults = {
        "llm": openai.LLM(model="gpt-4o-mini"),
        "turn_detection": "manual",  # Manual for testing
    }
    defaults.update(kwargs)
    return AgentSession(**defaults)


def create_mock_context() -> RunContext:
    """Create a mock RunContext for testing tools."""
    context = Mock(spec=RunContext)
    context.userdata = {}
    return context


# Fixtures for pytest

@pytest.fixture
async def test_llm():
    """Provide test LLM instance."""
    async with openai.LLM(model="gpt-4o-mini") as llm:
        yield llm


@pytest.fixture
async def test_session(test_llm):
    """Provide test session instance."""
    async with AgentSession(llm=test_llm) as session:
        yield session


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
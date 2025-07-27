"""
Test patterns specifically for function tools in LiveKit Agents.
"""

import pytest
from unittest.mock import Mock, patch
import json

from livekit.agents import RunContext, ToolError
from livekit.agents.testing import mock_tools

# Import tools to test
from examples.tool_enabled_agent.tools import (
    database_query,
    schedule_appointment,
    translate_text,
    generate_report,
    AVAILABLE_TOOLS,
)


class TestDatabaseQueryTool:
    """Test database query tool functionality."""
    
    @pytest.mark.asyncio
    async def test_valid_query(self):
        """Test querying valid table with filters."""
        context = Mock(spec=RunContext)
        
        result = await database_query(
            context,
            table="customers",
            filters={"status": "active"},
            limit=5
        )
        
        assert "Found" in result
        assert "customers" in result
        assert "active" in result
    
    @pytest.mark.asyncio
    async def test_invalid_table(self):
        """Test querying non-existent table."""
        context = Mock(spec=RunContext)
        
        with pytest.raises(ToolError) as exc_info:
            await database_query(
                context,
                table="invalid_table",
                filters={},
            )
        
        assert "not found" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_empty_results(self):
        """Test query with no matching results."""
        context = Mock(spec=RunContext)
        
        result = await database_query(
            context,
            table="customers",
            filters={"status": "deleted"},  # No mock data has this status
        )
        
        assert "No records found" in result


class TestScheduleAppointmentTool:
    """Test appointment scheduling tool."""
    
    @pytest.mark.asyncio
    async def test_valid_appointment(self):
        """Test scheduling valid future appointment."""
        context = Mock(spec=RunContext)
        
        # Use future date
        result = await schedule_appointment(
            context,
            date="2025-12-01",
            time="14:30",
            duration_minutes=60,
            description="Doctor visit"
        )
        
        assert "scheduled successfully" in result
        assert "APT-" in result
        assert "60 minutes" in result
        assert "Doctor visit" in result
    
    @pytest.mark.asyncio
    async def test_past_appointment(self):
        """Test scheduling appointment in the past."""
        context = Mock(spec=RunContext)
        
        with pytest.raises(ToolError) as exc_info:
            await schedule_appointment(
                context,
                date="2020-01-01",
                time="10:00",
            )
        
        assert "past" in str(exc_info.value).lower()
    
    @pytest.mark.asyncio
    async def test_invalid_datetime_format(self):
        """Test invalid date/time format."""
        context = Mock(spec=RunContext)
        
        with pytest.raises(ToolError) as exc_info:
            await schedule_appointment(
                context,
                date="01-12-2025",  # Wrong format
                time="14:30",
            )
        
        assert "Invalid date" in str(exc_info.value)


class TestTranslateTextTool:
    """Test translation tool."""
    
    @pytest.mark.asyncio
    async def test_supported_language(self):
        """Test translation to supported language."""
        context = Mock(spec=RunContext)
        
        result = await translate_text(
            context,
            text="Hello, how are you?",
            target_language="es",
        )
        
        assert "Spanish" in result
        assert "Original:" in result
        assert "Translated:" in result
    
    @pytest.mark.asyncio
    async def test_unsupported_language(self):
        """Test translation to unsupported language."""
        context = Mock(spec=RunContext)
        
        with pytest.raises(ToolError) as exc_info:
            await translate_text(
                context,
                text="Hello",
                target_language="xyz",  # Invalid language code
            )
        
        assert "Unsupported language" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_auto_detection(self):
        """Test translation with auto language detection."""
        context = Mock(spec=RunContext)
        
        result = await translate_text(
            context,
            text="Bonjour",
            target_language="en",
            source_language="auto",
        )
        
        # Should work even with auto detection
        assert "Translation" in result


class TestGenerateReportTool:
    """Test report generation tool."""
    
    @pytest.mark.asyncio
    async def test_sales_report(self):
        """Test generating sales report."""
        context = Mock(spec=RunContext)
        
        result = await generate_report(
            context,
            report_type="sales",
            start_date="2024-01-01",
            end_date="2024-01-31",
            format="summary"
        )
        
        assert "Sales Report" in result
        assert "total_sales" in result.lower()
        assert "2024-01-01 to 2024-01-31" in result
    
    @pytest.mark.asyncio
    async def test_invalid_date_range(self):
        """Test report with invalid date range."""
        context = Mock(spec=RunContext)
        
        with pytest.raises(ToolError) as exc_info:
            await generate_report(
                context,
                report_type="sales",
                start_date="2024-01-31",
                end_date="2024-01-01",  # End before start
            )
        
        assert "Start date must be before end date" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_json_format(self):
        """Test report in JSON format."""
        context = Mock(spec=RunContext)
        
        result = await generate_report(
            context,
            report_type="activity",
            start_date="2024-01-01",
            end_date="2024-01-31",
            format="json"
        )
        
        # Should be valid JSON
        data = json.loads(result)
        assert isinstance(data, dict)
        assert "total_activities" in data


class TestToolRegistry:
    """Test tool registry functionality."""
    
    def test_available_tools_list(self):
        """Test listing available tools."""
        from examples.tool_enabled_agent.tools import list_available_tools
        
        tools = list_available_tools()
        assert isinstance(tools, list)
        assert "database_query" in tools
        assert "schedule_appointment" in tools
        assert len(tools) >= 4
    
    def test_get_tool_by_name(self):
        """Test retrieving tool by name."""
        from examples.tool_enabled_agent.tools import get_tool_by_name
        
        # Valid tool
        tool = get_tool_by_name("database_query")
        assert tool is not None
        assert callable(tool)
        
        # Invalid tool
        tool = get_tool_by_name("non_existent_tool")
        assert tool is None


class TestToolMocking:
    """Test mocking patterns for tools."""
    
    @pytest.mark.asyncio
    async def test_mock_external_api(self):
        """Test mocking external API calls in tools."""
        context = Mock(spec=RunContext)
        
        # Mock the aiohttp session
        with patch('aiohttp.ClientSession') as mock_session:
            # Configure mock response
            mock_response = Mock()
            mock_response.status = 200
            mock_response.json = Mock(
                return_value={"temperature": 25, "conditions": "sunny"}
            )
            
            # Set up async context manager
            mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = mock_response
            
            # Tool should use mocked response
            # (In real tool, would need to actually use aiohttp)
            # This demonstrates the pattern
    
    @pytest.mark.asyncio
    async def test_mock_tool_in_agent(self):
        """Test mocking tools within agent context."""
        from examples.tool_enabled_agent.agent import ToolEnabledAgent
        
        # Define mock implementations
        mock_implementations = {
            "web_search": lambda **kwargs: "Mocked search results",
            "get_weather": lambda **kwargs: "Mocked weather: 75°F and sunny",
            "calculate": lambda **kwargs: "42",
        }
        
        # Use mock_tools context manager
        with mock_tools(ToolEnabledAgent, mock_implementations):
            agent = ToolEnabledAgent()
            context = Mock(spec=RunContext)
            
            # Tools should return mocked values
            result = await agent.web_search(context, "test query")
            assert result == "Mocked search results"
            
            result = await agent.get_weather(context, "NYC")
            assert "75°F and sunny" in result


class TestToolErrorHandling:
    """Test error handling patterns in tools."""
    
    @pytest.mark.asyncio
    async def test_tool_error_types(self):
        """Test different types of tool errors."""
        context = Mock(spec=RunContext)
        
        # User-friendly error
        with pytest.raises(ToolError) as exc_info:
            await database_query(context, "invalid_table", {})
        
        error_message = str(exc_info.value)
        assert "not found" in error_message
        # Should not expose internal details
        assert "Exception" not in error_message
        assert "Traceback" not in error_message
    
    @pytest.mark.asyncio
    async def test_tool_validation(self):
        """Test input validation in tools."""
        context = Mock(spec=RunContext)
        
        # Test with invalid input types
        with pytest.raises(Exception):  # Could be TypeError or ToolError
            await schedule_appointment(
                context,
                date=12345,  # Should be string
                time="10:00"
            )
    
    @pytest.mark.asyncio
    async def test_tool_timeout_handling(self):
        """Test handling timeouts in tools."""
        context = Mock(spec=RunContext)
        
        # Mock a timeout scenario
        with patch('asyncio.sleep') as mock_sleep:
            # Make sleep raise TimeoutError
            mock_sleep.side_effect = asyncio.TimeoutError()
            
            # Tools should handle timeouts gracefully
            # (Implementation depends on specific tool)


# Integration test example
class TestToolIntegration:
    """Test tools integrated with agents."""
    
    @pytest.mark.asyncio
    async def test_tool_chain(self):
        """Test chaining multiple tool calls."""
        from livekit.agents import AgentSession
        from livekit.plugins import openai
        
        # Create a test agent that uses multiple tools
        class ChainAgent(Agent):
            @function_tool
            async def step1(self, context: RunContext) -> str:
                return "Step 1 complete"
            
            @function_tool
            async def step2(self, context: RunContext, input: str) -> str:
                return f"Step 2 complete with: {input}"
        
        async with (
            openai.LLM(model="gpt-4o-mini") as llm,
            AgentSession(llm=llm) as session,
        ):
            await session.start(ChainAgent())
            
            result = await session.run(
                user_input="Execute both steps in order"
            )
            
            # Should call both tools
            result.expect.contains_function_call(name="step1")
            result.expect.contains_function_call(name="step2")


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
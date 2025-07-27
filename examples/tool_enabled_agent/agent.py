import logging
import aiohttp
import json
from datetime import datetime
from dotenv import load_dotenv

from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    WorkerOptions,
    cli,
    function_tool,
    RunContext,
    ToolError,
)
from livekit.agents.job import get_job_context
from livekit.plugins import deepgram, openai, silero

logger = logging.getLogger("tool-agent")

load_dotenv()


class ToolEnabledAgent(Agent):
    """Agent with multiple external tool integrations."""
    
    def __init__(self):
        super().__init__(
            instructions="You are a helpful assistant with access to various tools. "
            "You can search the web, perform calculations, check weather, "
            "and interact with external APIs. Be proactive in using tools to help users."
        )

    async def on_enter(self):
        await self.session.generate_reply(
            instructions="Greet the user and mention some of the tools you have available."
        )

    @function_tool
    async def web_search(
        self,
        context: RunContext,
        query: str,
        num_results: int = 3,
    ) -> str:
        """Search the web for information.
        
        Args:
            query: Search query
            num_results: Number of results to return (max 5)
        """
        logger.info(f"Web search: {query}")
        
        # Mock web search - replace with actual API (DuckDuckGo, Google, etc.)
        try:
            # In production, use actual search API
            mock_results = [
                {
                    "title": f"Result {i+1} for {query}",
                    "snippet": f"This is a relevant snippet about {query}...",
                    "url": f"https://example.com/{i+1}"
                }
                for i in range(min(num_results, 5))
            ]
            
            formatted_results = []
            for r in mock_results:
                formatted_results.append(
                    f"**{r['title']}**\n{r['snippet']}\n{r['url']}"
                )
            
            return "\n\n".join(formatted_results)
            
        except Exception as e:
            logger.error(f"Search error: {e}")
            raise ToolError("Unable to perform web search at this time")

    @function_tool
    async def calculate(
        self,
        context: RunContext,
        expression: str,
    ) -> str:
        """Perform mathematical calculations.
        
        Args:
            expression: Mathematical expression to evaluate
        """
        logger.info(f"Calculating: {expression}")
        
        try:
            # Safe evaluation of mathematical expressions
            # In production, use a proper math parser
            allowed_names = {
                "abs": abs, "round": round, "min": min, "max": max,
                "sum": sum, "pow": pow, "len": len,
            }
            
            # Remove dangerous characters
            if any(char in expression for char in ["import", "exec", "eval", "__"]):
                raise ToolError("Invalid expression")
            
            result = eval(expression, {"__builtins__": {}}, allowed_names)
            return f"The result of {expression} is {result}"
            
        except Exception as e:
            logger.error(f"Calculation error: {e}")
            raise ToolError(f"Unable to calculate: {str(e)}")

    @function_tool
    async def get_weather(
        self,
        context: RunContext,
        location: str,
        units: str = "fahrenheit",
    ) -> str:
        """Get current weather for a location.
        
        Args:
            location: City name or coordinates
            units: Temperature units (celsius or fahrenheit)
        """
        logger.info(f"Getting weather for {location} in {units}")
        
        try:
            # In production, use actual weather API
            async with aiohttp.ClientSession() as session:
                # Mock response - replace with actual API call
                weather_data = {
                    "location": location,
                    "temperature": 72 if units == "fahrenheit" else 22,
                    "conditions": "partly cloudy",
                    "humidity": 65,
                    "wind_speed": 10,
                    "wind_direction": "NW",
                }
                
                unit_symbol = "°F" if units == "fahrenheit" else "°C"
                
                return (
                    f"Weather in {weather_data['location']}:\n"
                    f"Temperature: {weather_data['temperature']}{unit_symbol}\n"
                    f"Conditions: {weather_data['conditions']}\n"
                    f"Humidity: {weather_data['humidity']}%\n"
                    f"Wind: {weather_data['wind_speed']} mph {weather_data['wind_direction']}"
                )
                
        except Exception as e:
            logger.error(f"Weather API error: {e}")
            raise ToolError("Unable to fetch weather data")

    @function_tool
    async def get_time(
        self,
        context: RunContext,
        timezone: str = "UTC",
    ) -> str:
        """Get current time in specified timezone.
        
        Args:
            timezone: Timezone name (e.g., "America/New_York", "Europe/London")
        """
        try:
            from zoneinfo import ZoneInfo
            
            tz = ZoneInfo(timezone)
            current_time = datetime.now(tz)
            
            return f"Current time in {timezone}: {current_time.strftime('%Y-%m-%d %H:%M:%S %Z')}"
            
        except Exception as e:
            logger.error(f"Timezone error: {e}")
            raise ToolError(f"Invalid timezone: {timezone}")

    @function_tool
    async def send_email_draft(
        self,
        context: RunContext,
        recipient: str,
        subject: str,
        body: str,
    ) -> str:
        """Create an email draft (not actually sent).
        
        Args:
            recipient: Email recipient
            subject: Email subject
            body: Email body content
        """
        logger.info(f"Creating email draft to {recipient}")
        
        # In production, integrate with email service
        draft = {
            "to": recipient,
            "subject": subject,
            "body": body,
            "created_at": datetime.now().isoformat(),
            "draft_id": "DRAFT-12345"
        }
        
        return (
            f"Email draft created:\n"
            f"To: {draft['to']}\n"
            f"Subject: {draft['subject']}\n"
            f"Draft ID: {draft['draft_id']}\n\n"
            f"The draft has been saved and can be reviewed before sending."
        )

    @function_tool
    async def get_user_location(
        self,
        context: RunContext,
    ) -> str:
        """Get user's location via RPC call to frontend.
        
        This demonstrates RPC tool forwarding to the client application.
        """
        try:
            room = get_job_context().room
            
            # Get first participant (user)
            participant_identity = next(iter(room.remote_participants))
            
            # Perform RPC call to client
            response = await room.local_participant.perform_rpc(
                destination_identity=participant_identity,
                method="getUserLocation",
                payload=json.dumps({}),
                response_timeout=5.0,
            )
            
            location_data = json.loads(response)
            return f"Your location: {location_data.get('city', 'Unknown')}, {location_data.get('country', 'Unknown')}"
            
        except Exception as e:
            logger.error(f"Location RPC error: {e}")
            raise ToolError("Unable to retrieve location. Please ensure location access is enabled.")


async def entrypoint(ctx: JobContext):
    await ctx.connect()
    
    session = AgentSession(
        vad=silero.VAD.load(),
        stt=deepgram.STT(model="nova-3"),
        llm=openai.LLM(
            model="gpt-4o-mini",
            temperature=0.7,  # Slightly lower for tool usage
        ),
        tts=openai.TTS(voice="nova"),
    )
    
    # Log tool usage
    @session.on("function_called")
    def on_function_called(ev):
        logger.info(f"Tool called: {ev.function_name} with args: {ev.arguments}")
    
    @session.on("function_call_failed")
    def on_function_failed(ev):
        logger.error(f"Tool failed: {ev.function_name} - {ev.error}")
    
    await session.start(
        agent=ToolEnabledAgent(),
        room=ctx.room,
    )


if __name__ == "__main__":
    cli.run_app(WorkerOptions(
        entrypoint_fnc=entrypoint
    ))
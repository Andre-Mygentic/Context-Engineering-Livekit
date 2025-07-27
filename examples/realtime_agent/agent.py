import logging
from dotenv import load_dotenv

from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    WorkerOptions,
    cli,
    function_tool,
    RunContext,
)
from livekit.plugins import openai
from livekit.plugins.openai import realtime
from openai.types.beta.realtime.session import TurnDetection

logger = logging.getLogger("realtime-agent")

load_dotenv()


class RealtimeAgent(Agent):
    def __init__(self):
        super().__init__(
            instructions="You are a natural conversational AI assistant. "
            "Speak with emotion, personality, and natural inflection. "
            "You can laugh, whisper, and emphasize words naturally. "
            "Keep responses concise and engaging."
        )

    async def on_enter(self):
        # Generate greeting with natural speech
        await self.session.generate_reply(
            instructions="Greet the user warmly and naturally, "
            "as if you're happy to meet them."
        )

    @function_tool
    async def get_weather(
        self, context: RunContext, location: str
    ) -> str:
        """Get current weather for a location.
        
        Args:
            location: City name or location
        """
        logger.info(f"Getting weather for {location}")
        
        # Mock weather data - replace with actual API
        weather_data = {
            "temperature": 68,
            "conditions": "partly cloudy",
            "humidity": 65,
            "wind": "5 mph"
        }
        
        return (
            f"The weather in {location} is {weather_data['temperature']} degrees "
            f"and {weather_data['conditions']}, with {weather_data['humidity']}% humidity "
            f"and winds at {weather_data['wind']}."
        )

    @function_tool
    async def tell_joke(self, context: RunContext) -> str:
        """Tell a funny joke to the user."""
        jokes = [
            "Why don't scientists trust atoms? Because they make up everything!",
            "What do you call a bear with no teeth? A gummy bear!",
            "Why did the scarecrow win an award? He was outstanding in his field!",
        ]
        
        import random
        return random.choice(jokes)


async def entrypoint(ctx: JobContext):
    """Main entry point for realtime agent."""
    await ctx.connect()
    logger.info(f"Connected to room: {ctx.room.name}")
    
    # Configure realtime model for speech-to-speech
    realtime_model = openai.realtime.RealtimeModel(
        model="gpt-4o-realtime-preview",
        voice="alloy",  # Options: alloy, echo, fable, onyx, nova, shimmer
        temperature=0.8,
        modalities=["text", "audio"],  # Support both text and audio
        turn_detection=TurnDetection(
            type="server_vad",  # Server-side voice activity detection
            threshold=0.5,
            prefix_padding_ms=300,
            silence_duration_ms=500,
            create_response=True,
            interrupt_response=True,  # Allow natural interruptions
        )
    )
    
    # Create session with only realtime model (no separate STT/TTS)
    session = AgentSession(
        llm=realtime_model,
    )
    
    # Log events for debugging
    @session.on("user_state_changed")
    def on_user_state(ev):
        logger.info(f"User state: {ev.new_state}")
    
    @session.on("agent_state_changed") 
    def on_agent_state(ev):
        logger.info(f"Agent state: {ev.new_state}")
    
    # Start the session
    await session.start(
        room=ctx.room,
        agent=RealtimeAgent()
    )
    
    logger.info("Realtime agent started successfully")


if __name__ == "__main__":
    cli.run_app(WorkerOptions(
        entrypoint_fnc=entrypoint
    ))
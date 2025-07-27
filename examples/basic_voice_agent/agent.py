import logging
from dotenv import load_dotenv

from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    JobProcess,
    RoomInputOptions,
    RoomOutputOptions,
    RunContext,
    WorkerOptions,
    cli,
    metrics,
)
from livekit.agents.llm import function_tool
from livekit.agents.voice import MetricsCollectedEvent
from livekit.plugins import deepgram, openai, silero
from livekit.plugins.turn_detector.multilingual import MultilingualModel

logger = logging.getLogger("basic-agent")

load_dotenv()


class MyAgent(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions="Your name is Kelly. You are a helpful voice assistant. "
            "Your responses should be concise and conversational. "
            "You are curious and friendly, with a warm personality."
        )

    async def on_enter(self):
        # Generate initial greeting when agent joins
        self.session.generate_reply()

    @function_tool
    async def lookup_weather(
        self, context: RunContext, location: str, latitude: str, longitude: str
    ):
        """Called when the user asks for weather information.
        Ensure the user's location (city or region) is provided.
        When given a location, estimate the latitude and longitude.

        Args:
            location: The location they are asking for
            latitude: The latitude of the location
            longitude: The longitude of the location
        """
        logger.info(f"Looking up weather for {location} ({latitude}, {longitude})")
        
        # In production, call actual weather API
        temperature = 72
        conditions = "sunny with a few clouds"
        
        return f"The weather in {location} is currently {temperature} degrees and {conditions}."

    @function_tool
    async def set_reminder(
        self, context: RunContext, reminder: str, time: str
    ):
        """Set a reminder for the user.
        
        Args:
            reminder: What to remind the user about
            time: When to remind them (e.g., "in 5 minutes", "tomorrow at 3pm")
        """
        logger.info(f"Setting reminder: {reminder} at {time}")
        
        # In production, integrate with reminder system
        return f"I've set a reminder to {reminder} {time}."


def prewarm(proc: JobProcess):
    """Preload heavy resources before job assignment."""
    proc.userdata["vad"] = silero.VAD.load()
    logger.info("VAD model preloaded")


async def entrypoint(ctx: JobContext):
    """Main entry point for the agent."""
    # Log context information
    ctx.log_context_fields = {
        "room": ctx.room.name,
    }
    
    # Connect to the room first
    await ctx.connect()
    logger.info(f"Connected to room: {ctx.room.name}")

    # Create agent session with voice pipeline
    session = AgentSession(
        vad=ctx.proc.userdata["vad"],
        stt=deepgram.STT(
            model="nova-3",
            language="multi"  # Multi-language support
        ),
        llm=openai.LLM(
            model="gpt-4o-mini",
            temperature=0.8
        ),
        tts=openai.TTS(
            voice="alloy",
            speed=1.0
        ),
        turn_detection=MultilingualModel(),
    )

    # Set up metrics collection
    usage_collector = metrics.UsageCollector()

    @session.on("metrics_collected")
    def _on_metrics_collected(ev: MetricsCollectedEvent):
        metrics.log_metrics(ev.metrics)
        usage_collector.collect(ev.metrics)

    async def log_usage():
        """Log usage summary on shutdown."""
        summary = usage_collector.get_summary()
        logger.info(f"Usage summary: {summary}")

    ctx.add_shutdown_callback(log_usage)

    # Start the session
    await session.start(
        agent=MyAgent(),
        room=ctx.room,
        room_input_options=RoomInputOptions(
            # Uncomment for noise cancellation
            # noise_cancellation=noise_cancellation.BVC(),
        ),
        room_output_options=RoomOutputOptions(
            transcription_enabled=True
        ),
    )


if __name__ == "__main__":
    cli.run_app(WorkerOptions(
        entrypoint_fnc=entrypoint,
        prewarm_fnc=prewarm
    ))
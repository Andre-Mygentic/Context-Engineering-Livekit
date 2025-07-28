import logging
import asyncio
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
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

logger = logging.getLogger("appointment-agent")

load_dotenv()


class AppointmentConfirmationAgent(Agent):
    """Professional receptionist agent for appointment confirmations."""
    
    def __init__(self, appointment_details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(
            instructions="""You are a polite, professional, yet warm-sounding receptionist named Sarah. 
            Your job is to call customers who already have booked appointments to check if they are 
            still able to attend. You are calling approximately 24 hours before their appointment 
            to confirm attendance and serve as a reminder.
            
            IMPORTANT CONVERSATIONAL BEHAVIORS:
            - Use natural filler phrases when thinking: "um", "let me see", "one moment"
            - Include acknowledgment sounds when listening: "mm-hmm", "I see", "got it"
            - Vary your responses to avoid sounding scripted
            - Add brief pauses when "looking up" information
            - Speak at a normal, conversational pace
            
            CONVERSATION APPROACH:
            - Start with a warm greeting and clearly identify yourself and your purpose
            - Confirm the appointment details (date, time, service)
            - If the customer confirms, thank them warmly and end the call
            - If they need to reschedule, acknowledge and provide next steps
            - If they seem confused, patiently clarify who you are and why you're calling
            
            ERROR RECOVERY:
            - If you don't understand, use natural phrases like "Sorry, could you repeat that?"
            - If still unclear after 2 attempts, try rephrasing your question
            - Never give up - keep trying different approaches until you get what you need
            - If someone says they're not the right person, politely ask for them
            
            Remember: You're a human receptionist, not a robot. Be natural, be helpful, be persistent."""
        )
        
        # Default appointment details for testing
        # In production, this would be passed in or fetched from a database
        self.appointment_details = appointment_details or {
            "date": "tomorrow at 2:30 PM",
            "service": "dental cleaning",
            "doctor": "Dr. Johnson",
            "location": "Main Street Dental Clinic",
            "patient_name": "there",  # Use "there" as fallback if no name
        }
        
        # Track conversation state
        self.confirmation_status = None  # Will be 'confirmed', 'rescheduled', 'cancelled'
        self.clarification_attempts = 0

    async def on_enter(self):
        """Called when agent first joins the call."""
        # Small delay to simulate picking up the phone naturally
        await asyncio.sleep(0.8)
        
        # Get time of day for natural greeting
        hour = datetime.now().hour
        time_of_day = "morning" if hour < 12 else "afternoon" if hour < 17 else "evening"
        
        # Generate initial greeting with appointment details
        greeting = f"""Good {time_of_day}! This is Sarah calling from {self.appointment_details['location']}. 
        I'm calling to confirm your appointment with {self.appointment_details['doctor']} 
        {self.appointment_details['date']} for your {self.appointment_details['service']}. 
        Are you still able to make it?"""
        
        # Use the session to speak the greeting
        await self.session.say(greeting)

    @function_tool
    async def confirm_appointment(
        self, context: RunContext
    ) -> str:
        """Called when the customer confirms they can make their appointment.
        
        This tool is triggered by affirmative responses like "yes", "I'll be there", 
        "confirmed", etc.
        """
        logger.info("Appointment confirmed")
        self.confirmation_status = "confirmed"
        
        return (
            "Perfect! I have you confirmed. We'll see you "
            f"{self.appointment_details['date']} for your {self.appointment_details['service']}. "
            "Thank you so much, and have a wonderful rest of your day!"
        )

    @function_tool
    async def handle_reschedule_request(
        self, context: RunContext
    ) -> str:
        """Called when the customer needs to reschedule their appointment.
        
        This tool is triggered by responses indicating they can't make it or 
        need a different time.
        """
        logger.info("Customer requesting reschedule")
        self.confirmation_status = "rescheduled"
        
        return (
            "I understand you need to reschedule. Let me help you with that. "
            "Would you like me to check what other times we have available this week, "
            "or would you prefer to call back when you know your schedule better?"
        )

    @function_tool
    async def handle_cancellation(
        self, context: RunContext
    ) -> str:
        """Called when the customer wants to cancel their appointment.
        
        This tool is triggered by clear cancellation requests.
        """
        logger.info("Customer requesting cancellation")
        self.confirmation_status = "cancelled"
        
        return (
            "I understand you need to cancel your appointment. I'll go ahead and "
            "cancel that for you. Would you like me to help you reschedule for "
            "another time, or would you prefer to call us back when you're ready?"
        )

    @function_tool
    async def clarify_appointment_details(
        self, context: RunContext,
        detail_type: str
    ) -> str:
        """Called when the customer asks for clarification about appointment details.
        
        Args:
            detail_type: What they're asking about (time, location, service, etc.)
        """
        logger.info(f"Clarifying {detail_type}")
        
        if detail_type == "time" or detail_type == "date":
            return f"Your appointment is scheduled for {self.appointment_details['date']}."
        elif detail_type == "location":
            return f"The appointment is at {self.appointment_details['location']}."
        elif detail_type == "service":
            return f"You're scheduled for a {self.appointment_details['service']} with {self.appointment_details['doctor']}."
        elif detail_type == "doctor":
            return f"Your appointment is with {self.appointment_details['doctor']}."
        else:
            # Provide all details
            return (
                f"Let me confirm all the details for you. You have a {self.appointment_details['service']} "
                f"with {self.appointment_details['doctor']} at {self.appointment_details['location']} "
                f"{self.appointment_details['date']}."
            )

    @function_tool
    async def handle_wrong_person(
        self, context: RunContext,
        requested_person: Optional[str] = None
    ) -> str:
        """Called when the person who answered isn't the patient.
        
        Args:
            requested_person: Name of the person they say we should speak to
        """
        logger.info(f"Wrong person answered, looking for: {requested_person}")
        
        if requested_person:
            return (
                f"Oh, I apologize! I'm looking for {requested_person}. "
                "This is Sarah from {self.appointment_details['location']} calling about "
                "their appointment tomorrow. Are they available?"
            )
        else:
            return (
                "I apologize for the confusion. I'm calling from "
                f"{self.appointment_details['location']} about an appointment "
                f"{self.appointment_details['date']}. May I ask who I'm speaking with?"
            )


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

    # In production, you might fetch appointment details from a database
    # based on room metadata or participant identity
    appointment_details = {
        "date": "tomorrow at 2:30 PM",
        "service": "dental cleaning", 
        "doctor": "Dr. Johnson",
        "location": "Main Street Dental Clinic",
        "patient_name": "there",  # Would be actual name in production
    }

    # Create agent session with voice pipeline
    session = AgentSession(
        vad=ctx.proc.userdata["vad"],
        stt=deepgram.STT(
            model="nova-3",
            language="multi",  # Multi-language support
            smart_format=True,  # Better formatting of numbers, dates
            punctuate=True,
            interim_results=True,  # For better perceived responsiveness
        ),
        llm=openai.LLM(
            model="gpt-4o-mini",
            temperature=0.8,  # Higher for more natural variation
        ),
        tts=openai.TTS(
            voice="nova",  # Most natural female voice
            speed=1.0,  # Normal speaking pace
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

    # Log function tool usage
    @session.on("function_called")
    def on_function_called(ev):
        logger.info(f"Tool called: {ev.function_name} with args: {ev.arguments}")

    # Start the session
    agent = AppointmentConfirmationAgent(appointment_details)
    await session.start(
        agent=agent,
        room=ctx.room,
        room_input_options=RoomInputOptions(
            # Uncomment for noise cancellation if needed
            # noise_cancellation=noise_cancellation.BVC(),
        ),
        room_output_options=RoomOutputOptions(
            transcription_enabled=True
        ),
    )

    # Log final status
    logger.info(f"Call completed. Status: {agent.confirmation_status}")


if __name__ == "__main__":
    cli.run_app(WorkerOptions(
        entrypoint_fnc=entrypoint,
        prewarm_fnc=prewarm
    ))
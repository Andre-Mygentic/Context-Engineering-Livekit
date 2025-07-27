import logging
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

from livekit import api
from livekit.agents import (
    Agent,
    AgentSession,
    ChatContext,
    JobContext,
    JobProcess,
    RoomInputOptions,
    RoomOutputOptions,
    RunContext,
    WorkerOptions,
    cli,
    function_tool,
    metrics,
)
from livekit.agents.job import get_job_context
from livekit.agents.voice import MetricsCollectedEvent
from livekit.plugins import deepgram, openai, silero

logger = logging.getLogger("multi-agent")

load_dotenv()


@dataclass
class CustomerData:
    """Shared data between agents."""
    name: Optional[str] = None
    account_number: Optional[str] = None
    issue_type: Optional[str] = None
    priority: int = 1
    interaction_count: int = 0


class IntakeAgent(Agent):
    """Initial agent that greets customers and gathers information."""
    
    def __init__(self):
        super().__init__(
            instructions="You are a friendly customer service representative. "
            "Your job is to greet customers, gather their name and the nature of their issue, "
            "then route them to the appropriate specialist. Be warm and professional."
        )

    async def on_enter(self):
        await self.session.generate_reply(
            instructions="Greet the customer warmly and ask how you can help them today."
        )

    @function_tool
    async def collect_customer_info(
        self,
        context: RunContext[CustomerData],
        name: str,
        issue: str,
    ) -> str:
        """Collect customer information for routing.
        
        Args:
            name: Customer's name
            issue: Brief description of their issue
        """
        context.userdata.name = name
        context.userdata.issue_type = issue
        context.userdata.interaction_count += 1
        
        logger.info(f"Customer info collected: {name}, Issue: {issue}")
        
        return f"Thank you {name}, I understand you need help with {issue}."

    @function_tool
    async def route_to_specialist(
        self,
        context: RunContext[CustomerData],
    ):
        """Route customer to appropriate specialist based on their issue."""
        issue = context.userdata.issue_type
        
        if not issue:
            return "I need to understand your issue first before routing you."
        
        # Determine routing based on issue type
        if any(word in issue.lower() for word in ["billing", "payment", "invoice", "charge"]):
            logger.info("Routing to billing specialist")
            return "I'll connect you with our billing specialist", BillingAgent(chat_ctx=self.chat_ctx)
        
        elif any(word in issue.lower() for word in ["technical", "error", "bug", "not working"]):
            logger.info("Routing to technical support")
            return "I'll connect you with technical support", TechnicalAgent(chat_ctx=self.chat_ctx)
        
        else:
            logger.info("Routing to general support")
            return "I'll connect you with a general support specialist", GeneralAgent(chat_ctx=self.chat_ctx)


class BillingAgent(Agent):
    """Specialist agent for billing and payment issues."""
    
    def __init__(self, chat_ctx: Optional[ChatContext] = None):
        super().__init__(
            instructions="You are a billing specialist. Help customers with payment issues, "
            "invoices, refunds, and billing questions. You have access to their account information. "
            "Be helpful and solution-oriented.",
            chat_ctx=chat_ctx  # Preserve conversation history
        )

    async def on_enter(self):
        await self.session.generate_reply(
            instructions="Introduce yourself as a billing specialist and acknowledge their billing concern."
        )

    @function_tool
    async def lookup_account_balance(
        self,
        context: RunContext[CustomerData],
    ) -> str:
        """Look up customer's account balance."""
        # Mock implementation - replace with actual API
        balance = 125.50
        return f"Your current balance is ${balance:.2f}"

    @function_tool
    async def process_refund(
        self,
        context: RunContext[CustomerData],
        amount: float,
        reason: str,
    ) -> str:
        """Process a refund for the customer.
        
        Args:
            amount: Refund amount
            reason: Reason for refund
        """
        logger.info(f"Processing refund: ${amount} for {reason}")
        # Mock implementation
        return f"I've processed a refund of ${amount:.2f} for {reason}. It will appear in 3-5 business days."

    @function_tool
    async def escalate_to_manager(
        self,
        context: RunContext[CustomerData],
    ):
        """Escalate to a manager for complex issues."""
        context.userdata.priority = 2
        return "Let me get a manager to help with this", ManagerAgent(chat_ctx=self.chat_ctx)


class TechnicalAgent(Agent):
    """Specialist agent for technical support."""
    
    def __init__(self, chat_ctx: Optional[ChatContext] = None):
        super().__init__(
            instructions="You are a technical support specialist. Help customers troubleshoot "
            "technical issues, errors, and system problems. Guide them through solutions step by step.",
            chat_ctx=chat_ctx
        )

    async def on_enter(self):
        await self.session.generate_reply(
            instructions="Introduce yourself as technical support and acknowledge their technical issue."
        )

    @function_tool
    async def run_diagnostics(
        self,
        context: RunContext[CustomerData],
        system: str,
    ) -> str:
        """Run diagnostics on a system.
        
        Args:
            system: System to diagnose
        """
        logger.info(f"Running diagnostics on {system}")
        # Mock implementation
        return f"Diagnostics complete for {system}. Found 2 minor issues that can be auto-resolved."

    @function_tool
    async def create_ticket(
        self,
        context: RunContext[CustomerData],
        description: str,
        priority: str = "normal",
    ) -> str:
        """Create a support ticket.
        
        Args:
            description: Issue description
            priority: Ticket priority (low, normal, high)
        """
        ticket_id = "TK-12345"
        return f"I've created ticket {ticket_id} with {priority} priority. Our team will follow up within 24 hours."


class GeneralAgent(Agent):
    """General support agent for miscellaneous issues."""
    
    def __init__(self, chat_ctx: Optional[ChatContext] = None):
        super().__init__(
            instructions="You are a general customer support agent. Help with various "
            "customer needs and questions. Be resourceful and helpful.",
            chat_ctx=chat_ctx
        )

    async def on_enter(self):
        await self.session.generate_reply(
            instructions="Acknowledge their request and offer to help."
        )


class ManagerAgent(Agent):
    """Manager agent for escalated issues."""
    
    def __init__(self, chat_ctx: Optional[ChatContext] = None):
        super().__init__(
            instructions="You are a customer service manager handling escalated issues. "
            "You have authority to approve special requests and resolve complex problems. "
            "Be empathetic and solution-focused.",
            chat_ctx=chat_ctx
        )

    async def on_enter(self):
        await self.session.generate_reply(
            instructions="Introduce yourself as a manager and express concern for their issue."
        )

    @function_tool
    async def approve_exception(
        self,
        context: RunContext[CustomerData],
        request: str,
    ) -> str:
        """Approve an exception request.
        
        Args:
            request: Description of the exception
        """
        logger.info(f"Manager approving exception: {request}")
        return f"I've approved your request for {request}. This is a one-time exception."

    @function_tool
    async def end_conversation(
        self,
        context: RunContext[CustomerData],
    ):
        """End the conversation after resolution."""
        await self.session.generate_reply(
            instructions=f"Thank {context.userdata.name} for their patience and confirm their issue is resolved.",
            allow_interruptions=False
        )
        
        # End the session
        job_ctx = get_job_context()
        await job_ctx.api.room.delete_room(api.DeleteRoomRequest(room=job_ctx.room.name))


def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()


async def entrypoint(ctx: JobContext):
    await ctx.connect()
    
    # Create session with shared customer data
    session = AgentSession[CustomerData](
        vad=ctx.proc.userdata["vad"],
        stt=deepgram.STT(model="nova-3"),
        llm=openai.LLM(model="gpt-4o-mini"),
        tts=openai.TTS(voice="echo"),  # Professional voice
        userdata=CustomerData(),  # Shared state
    )
    
    # Metrics collection
    usage_collector = metrics.UsageCollector()
    
    @session.on("metrics_collected")
    def _on_metrics_collected(ev: MetricsCollectedEvent):
        metrics.log_metrics(ev.metrics)
        usage_collector.collect(ev.metrics)
    
    # Log agent transitions
    @session.on("agent_updated")
    def on_agent_updated(agent):
        logger.info(f"Agent transitioned to: {type(agent).__name__}")
    
    # Shutdown logging
    async def log_usage():
        summary = usage_collector.get_summary()
        logger.info(f"Session summary: {summary}")
        logger.info(f"Total interactions: {session.userdata.interaction_count}")
    
    ctx.add_shutdown_callback(log_usage)
    
    # Start with intake agent
    await session.start(
        agent=IntakeAgent(),
        room=ctx.room,
        room_input_options=RoomInputOptions(),
        room_output_options=RoomOutputOptions(transcription_enabled=True),
    )


if __name__ == "__main__":
    cli.run_app(WorkerOptions(
        entrypoint_fnc=entrypoint,
        prewarm_fnc=prewarm
    ))
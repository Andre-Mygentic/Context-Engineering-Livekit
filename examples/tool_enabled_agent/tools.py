"""
Additional tool implementations that can be imported and used by agents.

This module demonstrates how to organize tools separately from the main agent code.
"""

import logging
import json
from typing import Dict, Any, List
from datetime import datetime, timedelta

from livekit.agents import function_tool, RunContext, ToolError

logger = logging.getLogger("agent-tools")


@function_tool
async def database_query(
    context: RunContext,
    table: str,
    filters: Dict[str, Any],
    limit: int = 10,
) -> str:
    """Query a database table with filters.
    
    Args:
        table: Table name to query
        filters: Dictionary of column:value filters
        limit: Maximum number of results
    """
    logger.info(f"Database query: {table} with filters {filters}")
    
    # Mock database query - replace with actual database connection
    try:
        # In production, use proper database connection with parameterized queries
        if table == "customers":
            mock_data = [
                {"id": 1, "name": "John Doe", "email": "john@example.com", "status": "active"},
                {"id": 2, "name": "Jane Smith", "email": "jane@example.com", "status": "active"},
            ]
        elif table == "orders":
            mock_data = [
                {"id": 101, "customer_id": 1, "total": 99.99, "status": "shipped"},
                {"id": 102, "customer_id": 2, "total": 149.99, "status": "pending"},
            ]
        else:
            raise ToolError(f"Table '{table}' not found")
        
        # Apply filters
        filtered_data = mock_data
        for key, value in filters.items():
            filtered_data = [row for row in filtered_data if row.get(key) == value]
        
        # Apply limit
        filtered_data = filtered_data[:limit]
        
        if not filtered_data:
            return f"No records found in {table} matching filters: {filters}"
        
        # Format results
        result = f"Found {len(filtered_data)} records in {table}:\n"
        for row in filtered_data:
            result += json.dumps(row, indent=2) + "\n"
        
        return result
        
    except Exception as e:
        logger.error(f"Database error: {e}")
        raise ToolError(f"Database query failed: {str(e)}")


@function_tool
async def schedule_appointment(
    context: RunContext,
    date: str,
    time: str,
    duration_minutes: int = 30,
    description: str = "",
) -> str:
    """Schedule an appointment.
    
    Args:
        date: Date in YYYY-MM-DD format
        time: Time in HH:MM format
        duration_minutes: Appointment duration
        description: Appointment description
    """
    try:
        # Parse date and time
        appointment_datetime = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
        end_time = appointment_datetime + timedelta(minutes=duration_minutes)
        
        # Check if in future
        if appointment_datetime < datetime.now():
            raise ToolError("Cannot schedule appointments in the past")
        
        # Mock appointment creation
        appointment = {
            "id": "APT-" + datetime.now().strftime("%Y%m%d%H%M%S"),
            "start": appointment_datetime.isoformat(),
            "end": end_time.isoformat(),
            "duration": duration_minutes,
            "description": description,
            "status": "confirmed"
        }
        
        logger.info(f"Appointment scheduled: {appointment}")
        
        return (
            f"Appointment scheduled successfully!\n"
            f"ID: {appointment['id']}\n"
            f"Date: {appointment_datetime.strftime('%A, %B %d, %Y')}\n"
            f"Time: {appointment_datetime.strftime('%I:%M %p')} - {end_time.strftime('%I:%M %p')}\n"
            f"Duration: {duration_minutes} minutes\n"
            f"{'Description: ' + description if description else ''}"
        )
        
    except ValueError as e:
        raise ToolError(f"Invalid date or time format: {str(e)}")
    except Exception as e:
        logger.error(f"Scheduling error: {e}")
        raise ToolError(f"Failed to schedule appointment: {str(e)}")


@function_tool
async def translate_text(
    context: RunContext,
    text: str,
    target_language: str,
    source_language: str = "auto",
) -> str:
    """Translate text to another language.
    
    Args:
        text: Text to translate
        target_language: Target language code (e.g., 'es', 'fr', 'de')
        source_language: Source language code or 'auto' for detection
    """
    logger.info(f"Translating to {target_language}: {text[:50]}...")
    
    # Mock translation - in production use translation API
    language_names = {
        "es": "Spanish",
        "fr": "French",
        "de": "German",
        "it": "Italian",
        "pt": "Portuguese",
        "ja": "Japanese",
        "ko": "Korean",
        "zh": "Chinese",
    }
    
    if target_language not in language_names:
        raise ToolError(f"Unsupported language: {target_language}")
    
    # Mock translations
    mock_translations = {
        "es": "Hola, ¿cómo estás?",
        "fr": "Bonjour, comment allez-vous?",
        "de": "Hallo, wie geht es dir?",
    }
    
    translation = mock_translations.get(
        target_language,
        f"[Translation to {language_names[target_language]}]: {text}"
    )
    
    return (
        f"Translation to {language_names[target_language]}:\n"
        f"Original: {text}\n"
        f"Translated: {translation}"
    )


@function_tool
async def generate_report(
    context: RunContext,
    report_type: str,
    start_date: str,
    end_date: str,
    format: str = "summary",
) -> str:
    """Generate various types of reports.
    
    Args:
        report_type: Type of report (sales, activity, performance)
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        format: Report format (summary, detailed, csv)
    """
    logger.info(f"Generating {report_type} report from {start_date} to {end_date}")
    
    try:
        # Validate dates
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        
        if start > end:
            raise ToolError("Start date must be before end date")
        
        # Mock report generation
        if report_type == "sales":
            data = {
                "total_sales": 45678.90,
                "transactions": 234,
                "average_sale": 195.21,
                "top_product": "Widget Pro",
            }
        elif report_type == "activity":
            data = {
                "total_activities": 1523,
                "unique_users": 89,
                "peak_hour": "2:00 PM",
                "most_common_action": "view_product",
            }
        else:
            data = {"status": "Report generated"}
        
        # Format report
        if format == "summary":
            report = f"# {report_type.title()} Report\n"
            report += f"Period: {start_date} to {end_date}\n\n"
            for key, value in data.items():
                report += f"- {key.replace('_', ' ').title()}: {value}\n"
        else:
            report = json.dumps(data, indent=2)
        
        return report
        
    except ValueError as e:
        raise ToolError(f"Invalid date format: {str(e)}")
    except Exception as e:
        logger.error(f"Report generation error: {e}")
        raise ToolError(f"Failed to generate report: {str(e)}")


# Tool registry for dynamic loading
AVAILABLE_TOOLS = {
    "database_query": database_query,
    "schedule_appointment": schedule_appointment,
    "translate_text": translate_text,
    "generate_report": generate_report,
}


def get_tool_by_name(name: str):
    """Get a tool function by name."""
    return AVAILABLE_TOOLS.get(name)


def list_available_tools() -> List[str]:
    """List all available tool names."""
    return list(AVAILABLE_TOOLS.keys())
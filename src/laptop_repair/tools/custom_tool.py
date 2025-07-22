# src/laptop_repair/tools/custom_tool.py

import subprocess
from typing import Type

# Import directly from pydantic, not pydantic.v1
from pydantic import BaseModel, Field
from crewai.tools import BaseTool


def _get_allowed_commands():
    """Returns a list of safe, approved commands."""
    return [
        "systeminfo",
        "tasklist",
        "wmic process get name,commandline,processid"
    ]

# Define a structured input schema for the tool.
class SystemCommandInput(BaseModel):
    """Input schema for the System Diagnostic Tool."""
    command: str = Field(description=f"The specific, safe command to execute. Must be one of: {', '.join(_get_allowed_commands())}.")

class SystemCommandTool(BaseTool):
    """
    A standard crewAI tool to execute specific, safe system diagnostic commands.
    """
    name: str = "System Diagnostic Command Executor"
    description: str = "Executes a specific, safe, read-only system command to gather raw diagnostic data for analysis."
    args_schema: Type[BaseModel] = SystemCommandInput

    def _run(self, command: str) -> str:
        """This method is called by the agent to execute the tool."""
        try:
            # Security check to only allow approved read-only commands
            if command.lower() not in _get_allowed_commands():
                return f"Error: The command '{command}' is not permitted for security reasons."

            # Execute the command using subprocess
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                errors='ignore'
            )
            stdout, stderr = process.communicate(timeout=60)

            if process.returncode != 0:
                return f"Error executing command: {stderr}"

            # Return the raw output directly. The agent is responsible for analysis.
            return f"--- Raw Output for command '{command}' ---\n{stdout}"

        except subprocess.TimeoutExpired:
            return f"Error: The command '{command}' timed out after 60 seconds."
        except Exception as e:
            return f"An unexpected error occurred while running the command: {e}"
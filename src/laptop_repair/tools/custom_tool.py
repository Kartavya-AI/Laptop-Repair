# src/laptop_repair/tools/custom_tool.py

import subprocess
from typing import Type

# Import directly from pydantic, not pydantic.v1
from pydantic import BaseModel, Field
from crewai.tools import BaseTool


def _get_allowed_commands():
    """Returns a list of safe, approved diagnostic commands."""
    return [
        "systeminfo",
        "tasklist",
        "wmic process get name,commandline,processid",
        "wmic logicaldisk get size,freespace,caption",
        "wmic memorychip get capacity,speed,manufacturer",
        "wmic cpu get name,maxclockspeed,numberofcores",
        "netstat -an",
        "ipconfig /all",
        "sfc /verifyonly",
        "chkdsk c: /f /r /x",  # Read-only check
        "dism /online /cleanup-image /checkhealth",
        "powercfg /batteryreport",
        "msinfo32 /report temp_report.txt",
        "wmic startup get caption,command,location",
        "wmic service where state='running' get name,displayname,processid"
    ]

def _get_safe_fix_commands():
    """Returns a list of safe commands that can be used in batch scripts."""
    return {
        # Disk cleanup commands
        "disk_cleanup": [
            "cleanmgr /sagerun:1",
            "del /q /f %temp%\\*.*",
            "rd /s /q %temp%",
            "md %temp%"
        ],
        # System file checker
        "system_files": [
            "sfc /scannow"
        ],
        # DISM repair
        "system_repair": [
            "dism /online /cleanup-image /restorehealth"
        ],
        # Services restart
        "restart_services": [
            "net stop spooler",
            "net start spooler",
            "net stop bits",
            "net start bits"
        ],
        # Network reset
        "network_reset": [
            "ipconfig /flushdns",
            "netsh winsock reset",
            "netsh int ip reset"
        ],
        # Performance optimization
        "performance_boost": [
            "powercfg /setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c",  # High performance
            "defrag c: /o"
        ]
    }

# Define a structured input schema for the tool.
class SystemCommandInput(BaseModel):
    """Input schema for the System Diagnostic Tool."""
    command: str = Field(description=f"The specific, safe command to execute. Must be one of: {', '.join(_get_allowed_commands())}.")

class SystemCommandTool(BaseTool):
    """
    A standard crewAI tool to execute specific, safe system diagnostic commands.
    """
    name: str = "System Diagnostic Command Executor"
    description: str = "Executes a specific, safe, read-only system command to gather raw diagnostic data for analysis. Can also suggest safe fix commands for batch script generation."
    args_schema: Type[BaseModel] = SystemCommandInput

    def _run(self, command: str) -> str:
        """This method is called by the agent to execute the tool."""
        try:
            # Special command to get available fix commands
            if command.lower() == "get_fix_commands":
                fix_commands = _get_safe_fix_commands()
                result = "Available safe fix command categories:\n"
                for category, commands in fix_commands.items():
                    result += f"\n{category.upper()}:\n"
                    for cmd in commands:
                        result += f"  - {cmd}\n"
                return result

            # Security check to only allow approved read-only commands
            allowed_commands = _get_allowed_commands()
            if not any(command.lower().startswith(allowed_cmd.lower()) for allowed_cmd in allowed_commands):
                return f"Error: The command '{command}' is not permitted for security reasons. Allowed commands: {', '.join(allowed_commands)}"

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
            stdout, stderr = process.communicate(timeout=120)  # Increased timeout

            if process.returncode != 0 and stderr:
                return f"Command completed with warnings: {stderr}\nOutput: {stdout}"

            # Return the raw output directly. The agent is responsible for analysis.
            return f"--- Raw Output for command '{command}' ---\n{stdout}"

        except subprocess.TimeoutExpired:
            return f"Error: The command '{command}' timed out after 120 seconds."
        except Exception as e:
            return f"An unexpected error occurred while running the command: {e}"

    def get_safe_fix_commands(self):
        """Public method to get safe fix commands for batch script generation."""
        return _get_safe_fix_commands()
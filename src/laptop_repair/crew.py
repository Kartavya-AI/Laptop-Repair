import os
import yaml
from crewai import Agent, Task, Crew, Process, LLM
from src.laptop_repair.tools.custom_tool import SystemCommandTool

def load_yaml(file_path: str) -> dict:
    """Helper function to load a YAML file."""
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

class LaptopRepairCrew:
    def __init__(self, problem_description: str):
        self.problem_description = problem_description
        # Path to the config files (assuming they are in a 'config' subdirectory)
        self.config_path = os.path.join(os.path.dirname(__file__), 'config')

        # Retrieve API key from environment variable
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set. Please provide the API key.")
            
        # 2. Instantiate the real Gemini LLM
        self.llm = LLM(model="gemini/gemini-1.5-flash-latest", api_key = api_key)

    def run(self):
        """
        Initializes and runs the crew with configurations loaded from YAML files.
        """
        # Load agent and task configurations from YAML
        agents_config = load_yaml(os.path.join(self.config_path, 'agents.yaml'))
        tasks_config = load_yaml(os.path.join(self.config_path, 'tasks.yaml'))
 
        # Instantiate your custom tool
        system_tool = SystemCommandTool()

        # --- Create a single, capable Agent ---
        lead_diagnostician = Agent(
            **agents_config['lead_diagnostician_agent'],
            tools=[system_tool],
            llm=self.llm, # Use the real LLM instance
            verbose=True,
            allow_delegation=False
        )

        # --- Create a focused Task for the agent ---
        system_analysis_task = Task(
            **tasks_config['system_analysis_task'],
            agent=lead_diagnostician
        )

        # 3. Assemble a simplified and robust Crew
        crew = Crew(
            agents=[lead_diagnostician],
            tasks=[system_analysis_task],
            process=Process.sequential,
            verbose=True
        )

        print("Laptop Repair Crew: Starting diagnosis...")
        # Use the kickoff method to start the crew's execution
        result = crew.kickoff(inputs={'problem_description': self.problem_description})
        print("Laptop Repair Crew: Diagnosis complete.")
        return result
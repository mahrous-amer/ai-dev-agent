import os
import json
from crewai import Agent
from config.settings import Settings

class AgentLoader:
    def __init__(self, folder_path=Settings.AGENTS_FOLDER):
        self.folder_path = folder_path
        self.llm = Settings.get_llm()

    def load_agents(self) -> dict:
        """
        Load agents from a specified folder containing JSON files.

        Returns:
            dict: A dictionary mapping agent roles to Agent objects.
        """
        agents = []
        for filename in os.listdir(self.folder_path):
            if filename.endswith(".json"):
                filepath = os.path.join(self.folder_path, filename)
                with open(filepath, "r") as f:
                    try:
                        agent_data = json.load(f)
                        agent = Agent(
                            name=agent_data["name"],
                            role=agent_data["role"],
                            goal=agent_data["goal"],
                            backstory=agent_data["backstory"],
                            llm=self.llm
                        )
                        agents.append(agent)
                    except Exception as e:
                        print(f"⚠️ Failed to load {filename}: {e}")
        return {agent.role.lower(): agent for agent in agents}

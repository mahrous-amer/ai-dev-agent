import os
import re
import logging
import asyncio
from pathlib import Path
from crewai import Task, Crew
from core.github_handler import GitHubHandler
from core.test_manager import TestManager
from core.agent_loader import AgentLoader
from core.documentation_generator import DocumentationGenerator
from config.settings import Settings

logger = logging.getLogger("Main")

class TaskExecutor:
    def __init__(self, task_name, task_desc):
        self.task_name = task_name
        self.task_desc = task_desc
        self.agent_loader = AgentLoader()
        self.agents_role_map = self.agent_loader.load_agents()
        self.github_handler = GitHubHandler()
        self.test_manager = TestManager()
        self.documentation_generator = DocumentationGenerator()
        self.developer_agent = self.agents_role_map.get("developer")
        self.tester_agent = self.agents_role_map.get("tester")
        self.doc_agent = self.agents_role_map.get("documenter")

    def slugify(self, text: str) -> str:
        """Convert task name into filesystem-friendly slug."""
        return re.sub(r'[^\w-]', '', text.lower().replace(" ", "-"))

    async def execute(self):
        task_slug = self.slugify(self.task_name)
        code_file = f"code_{task_slug}.py"
        test_file = f"test_{task_slug}.py"
        readme_file = f"readme_{task_slug}.md"

        issue_number = await self.github_handler.create_issue(self.task_name, self.task_desc)
        test_code = self.test_manager.generate_test_code(self.task_name, self.task_desc, self.tester_agent)

        with open(test_file, "w") as f:
            f.write(test_code)

        dev_task = Task(
            name=f"{self.task_name} - Code",
            description=self.task_desc,
            agent=self.developer_agent,
            expected_output="Complete, async capable, production grade code implementation."
        )
        test_summary_task = Task(
            name=f"{self.task_name} - Test Review",
            description="Provide insights into coverage and edge cases in the test suite.",
            agent=self.tester_agent,
            expected_output="Summary of test coverage effectiveness."
        )
        doc_task = Task(
            name=f"{self.task_name} - Documentation",
            description="Generate README using markdown and Mermaid diagrams.",
            agent=self.doc_agent,
            expected_output="Feature README in markdown with diagrams and integration examples."
        )

        crew = Crew(
            agents=[self.developer_agent, self.tester_agent, self.doc_agent],
            tasks=[dev_task, test_summary_task, doc_task],
            memory=True,
            verbose=True,
            planning=True
        )
        result = crew.kickoff()
        responses = {
            'developer_agent': {'filename': code_file, 'content': None},
            'tester_agent': {'filename': test_file, 'content': None},
            'doc_agent': {'filename': readme_file, 'content': None}
        }

        if hasattr(result, "results") and isinstance(result.results, list) and result.results:
            if hasattr(result.results[0], "output"):
                responses['developer_agent']['content'] = result.results[0].output
            else:
                logger.warning("⚠️ Developer agent output is not valid.")
                responses['developer_agent']['content'] = str(result.results[0])

            if hasattr(result.results[1], "output"):
                responses['tester_agent']['content'] = result.results[1].output
            else:
                logger.warning("⚠️ Tester agent output is not valid.")
                responses['tester_agent']['content'] = str(result.results[1])

            if hasattr(result.results[2], "output"):
                responses['doc_agent']['content'] = result.results[2].output
            else:
                logger.warning("⚠️ Doc agent output is not valid.")
                responses['doc_agent']['content'] = str(result.results[2])
        else:
            raise ValueError("❌ Crew output contains no usable results.")

        try:
            for agent, response in responses.items():
                if response['content']:
                    with open(response['filename'], "w") as f:
                        f.write(response['content'])
        except Exception as e:
            logger.warning("⚠️ Docstring generation failed: %s", e)

        test_results = self.test_manager.run_tests(test_file)
        logger.info(test_results)

        if test_results["exit_code"] != 0:
            logger.warning("❌ Tests failed. Aborting deployment.")
            return

        branch_name = f"feature/{task_slug}-ai"
        await self.github_handler.push_code(code_file, branch_name)
        await self.github_handler.push_code(test_file, branch_name)
        await self.github_handler.push_code(readme_file, branch_name)

        pr_number = await self.github_handler.create_pull_request(self.task_name, branch_name, issue_number)

        from cli import review_task
        if review_task() == "APPROVED":
            logger.info("✅ Pull Request Approved and ready.")
        else:
            logger.info("🛠️ Revisions needed. AI will re-iterate.")

if __name__ == "__main__":
    Settings.validate()
    task_name = "Website Endpoint Finder"
    task_desc = (
        "Create a Python script that recursively crawls a target website and finds all available endpoints."
        "The script should follow internal links, avoid going off-domain, and return a list of discovered URLs."
        "It should handle both static and dynamic links where possible and optionally detect API routes (e.g., /api/...)."
        "Focus on modular, testable code with docstrings to support further integration."
    )
    executor = TaskExecutor(task_name, task_desc)
    asyncio.run(executor.execute())

import subprocess
from typing import Optional, Dict, Any
from crewai import Crew, Task
from config.settings import Settings

class TestManager:
    def generate_test_code(self, function_name: str, function_description: str, tester_agent=None) -> str:
        prompt = f"""
        Write comprehensive `pytest` unit tests in Python for a function named **{function_name}**.
        The function should: {function_description}.
        
        Requirements:
        - Cover both typical and edge cases
        - Use descriptive test case names
        - Do not implement the function itself
        - Return only valid Python unit test code
        """

        if tester_agent:
            test_task = Task(
                name=f"Write tests for {function_name}",
                description=prompt,
                agent=tester_agent,
                expected_output="Valid pytest test code for the proposed function."
            )
            temp_crew = Crew(agents=[tester_agent], tasks=[test_task])
            result = temp_crew.kickoff()
            return result.output if hasattr(result, "output") else str(result)
        
        return {
            "output": "",
            "errors": "❌ Test agent does not exist.",
            "passed": 0,
            "failed": 0,
            "summary": "❌ Test agent does not exist.",
            "exit_code": 1
        }

    def run_tests(self, test_file: Optional[str] = None) -> Dict[str, Any]:
        test_target = test_file if test_file else "."

        try:
            result = subprocess.run(
                ["pytest", test_target, "--tb=short", "-q"],
                capture_output=True,
                text=True
            )

            passed = result.stdout.count("PASSED")
            failed = result.stdout.count("FAILED")

            return {
                "output": result.stdout.strip(),
                "errors": result.stderr.strip(),
                "passed": passed,
                "failed": failed,
                "summary": f"{passed} passed, {failed} failed",
                "exit_code": result.returncode
            }

        except Exception as e:
            return {
                "output": "",
                "errors": str(e),
                "passed": 0,
                "failed": 0,
                "summary": "❌ Test runner error occurred.",
                "exit_code": 1
            }

    def explain_test_failures(self, test_output: str, tester_agent=None) -> str:
        prompt = f"""
        The following pytest output contains failed tests. Analyze and explain the reasons for failure.
        Provide a list of actionable fixes.

        ----
        {test_output}
        ----
        """

        if tester_agent:
            analysis_task = Task(
                name="Explain failing tests",
                description=prompt,
                agent=tester_agent,
                expected_output="A clear and concise explanation of what caused the test failures and how to fix them."
            )
            temp_crew = Crew(
                agents=[tester_agent],
                tasks=[analysis_task]
            )
            return temp_crew.kickoff()

        return Settings.get_llm().predict(prompt)

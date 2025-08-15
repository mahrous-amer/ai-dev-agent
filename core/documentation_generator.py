from config.settings import Settings

class DocumentationGenerator:
    def generate_function_docstring(self, function_code: str) -> str:
        """
        Generate a docstring for a given Python function code.

        Args:
            function_code (str): The source code of the Python function.

        Returns:
            str: The generated docstring for the function.
        """
        prompt = f"Generate proper docstrings for the following Python function:\n\n{function_code}\n"
        return Settings.get_llm().predict(prompt)

    def generate_readme(self, feature_name: str, feature_description: str) -> str:
        """
        Generate a README document for a given feature.

        Args:
            feature_name (str): The name of the feature.
            feature_description (str): A detailed description of the feature.

        Returns:
            str: The generated README content.
        """
        prompt = f"Write a README doc explaining the feature `{feature_name}`:\n\n{feature_description}\n"
        return Settings.get_llm().predict(prompt)

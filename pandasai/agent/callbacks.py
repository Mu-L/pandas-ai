from ..prompts import FileBasedPrompt


class Callbacks:
    def __init__(self, agent_core):
        self.core = agent_core

    def on_prompt_generation(self, prompt: FileBasedPrompt) -> str:
        """
        A method to be called after prompt generation.

        Args:
            prompt (str): A prompt
        """
        self.core.last_prompt = str(prompt)

    def on_code_generation(self, code: str):
        """
        A method to be called after code generation.

        Args:
            code (str): A python code
        """
        self.core.last_code_generated = code

    def on_code_execution(self, code: str):
        """
        A method to be called after code execution.

        Args:
            code (str): A python code
        """
        self.core.last_code_executed = code

    def on_result(self, result):
        """
        A method to be called after code execution.

        Args:
            result (Any): A python code
        """
        self.core.last_result = result
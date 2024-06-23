import anthropic
import os
import git
import sys
from typing import List
from utils import run_bash_command, modify_file, create_branch_and_commit, run_main_file
from parser import parse_response

INITIAL_PROMPT = """
You are an AI assistant specialized in code analysis, modification, and optimization. Your tasks include:

1. Analyzing Python code and suggesting improvements
2. Running bash commands and interpreting their output
3. Modifying files and committing changes to Git repositories
4. Running and testing Python scripts

When responding, use the following prefixes for specific actions:
- "bash:" to execute a bash command
- "modify:" to modify a file, followed by the file path and new content
- "analyze:" to provide code analysis and suggestions

use the following patterns,
"bash": r"```bash\n(.*?)```",
"modify": r"```modify\n(.*?)\n---\n(.*?)```",
"analyze": r"```analyze\n(.*?)```"

You can make only one action at a time, and should not spend many tokens when writing only codes to run actions. Write only the essential.

Rules and limitations:
1. You can only run commands on files that already exist.
2. All file operations must be within the current working directory or its subdirectories.
3. You cannot create new files, only modify existing ones.
4. Bash commands are limited to: ls, cat, grep, head, tail, wc, diff, find, sort, uniq
5. You cannot use sudo or execute potentially harmful commands.
6. When modifying files, you can only change the content, not rename or move them.

Always provide clear explanations for your actions and recommendations.

The user may request either a command-only response or a detailed explanation. Adjust your response accordingly.
"""

class AIAssistant:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=os.getenv("API_KEY"))
        self.conversation_history: List[dict] = []

    def process_user_input(self, user_input: str, command_only: bool) -> str:
        self.conversation_history.append({
            "role": "user",
            "content": [{"type": "text", "text": user_input}]
        })

        response = self.client.messages.create(
            model="claude-3-sonnet-20240229",
            temperature=0,
            system=INITIAL_PROMPT,
            max_tokens=1024,
            messages=self.conversation_history
        )
        print(response)
        action, param1, param2 = parse_response(response.content[0].text)
        result = ""

        try:
            if action == "bash":
                result = run_bash_command(param1)
            elif action == "modify":
                modify_file(param1, param2)
                result = f"File {param1} has been modified."

                repo_path = os.path.dirname(param1)
                branch_name = f"claude_modification_{os.path.basename(param1)}"
                create_branch_and_commit(repo_path, branch_name, param1, "Claude's modification")
                result += f"\nChanges committed to new branch: {branch_name}"

                main_file = input("Enter the path to the main file to test: ")
                test_result = run_main_file(main_file)
                result += f"\nTest result:\n{test_result}"
            elif action == "analyze":
                result = f"Analysis:\n{param1}"
        except Exception as e:
            result = f"An error occurred: {str(e)}"

        if command_only:
            return result

        self.conversation_history[-1]["content"][0]["text"] += f"\n\nCommand output:\n{result}"

        final_response = self.client.messages.create(
            model="claude-3-sonnet-20240229",
            temperature=0,
            system=INITIAL_PROMPT,
            max_tokens=1024,
            messages=self.conversation_history
        )

        self.conversation_history.append({
            "role": "assistant",
            "content": [{"type": "text", "text": final_response.content[0].text}]
        })

        return final_response.content[0].text

if __name__ == "__main__":
    assistant = AIAssistant()
    command_only = sys.argv[1] == "@"
    user_input = " ".join(sys.argv[2:] if command_only else sys.argv[1:])
    response = assistant.process_user_input(user_input, command_only)
    print(response)

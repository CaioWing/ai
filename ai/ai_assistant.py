import anthropic
import os
import sys
import json
import subprocess
from typing import List, Dict
from loguru import logger
from prompt_toolkit import PromptSession
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.shortcuts import input_dialog, message_dialog
from prompt_toolkit.styles import Style

from utils import run_bash_command, modify_file, run_main_file
from parser import parse_response
from config import INITIAL_PROMPT, STYLE

import os
os.path.dirname(__file__)

class AIAssistant:
    def __init__(self, model_id: str):
        self.client = anthropic.Anthropic(api_key=os.getenv("CLAUDE_API"))
        self.current_directory = os.getcwd()
        self.conversation_history: List[dict] = []
        self.history_file = ".history"
        self.model_id = model_id
        self.load_history()

        logger.remove()
        logger.add(
            sys.stderr,
            format="<level>{level: <8}</level> | {message}",
            colorize=True
        )

        self.session = PromptSession()
        self.style = STYLE

    def load_history(self):
        if os.path.exists(self.history_file):
            with open(self.history_file, "r") as f:
                self.conversation_history = json.load(f)
        logger.info("Conversation history loaded")

    def save_history(self):
        with open(self.history_file, "w") as f:
            json.dump(self.conversation_history, f, indent=4)
        logger.info("Conversation history saved")

    def get_prompt(self):
        username = os.getenv("USER", "user")
        hostname = os.uname().nodename
        return HTML(
            f'<username>{username}</username>'
            f'<at>@</at>'
            f'<host>{hostname}</host>'
            f'<colon>:</colon>'
            f'<path>{self.current_directory}</path>'
            f'<pound>$</pound> '
        )

    def process_user_input(self, user_input: str) -> str:
        if user_input.startswith('cd '):
            new_dir = user_input[3:].strip()
            try:
                os.chdir(os.path.expanduser(new_dir))
                self.current_directory = os.getcwd()
                return f"Changed directory to: {self.current_directory}"
            except FileNotFoundError:
                return f"Directory not found: {new_dir}"
            except PermissionError:
                return f"Permission denied: {new_dir}"

        if user_input.startswith('load_file '):
            file_path = user_input[10:].strip()
            return self.load_file_content(file_path)

        if self.conversation_history and self.conversation_history[-1]["role"] == "user":
            self.conversation_history[-1]["content"][0]["text"] += f"\n\n{user_input}"
        else:
            self.conversation_history.append({
                "role": "user",
                "content": [{"type": "text", "text": user_input}]
            })

        results = []
        response = self.client.messages.create(
            model=self.model_id,
            temperature=0,
            system=INITIAL_PROMPT,
            max_tokens=1000,
            messages=self.conversation_history
        )

        parsed_actions = parse_response(response.content[0].text)
        additional_info = ''
        for action, details in parsed_actions:
            if action == "getting_info":
                info_commands = details['content'].strip().split('\n')
                info_results = []
                for info_command in info_commands:
                    info_result = run_bash_command(info_command)
                    info_results.append(f"Command: {info_command}\nResult: {info_result}")

                results.extend(info_results)
                additional_info = "Additional info:\n" + "\n".join(info_results) + "\n generated by code"

            elif action in ["bash", "modify", "analyze", "info"]:
                result = self.execute_single_action(action, details)
                results.append(result)

        self.conversation_history.append({
            "role": "assistant",
            "content": [
                {
                    "type": "text",
                    "text": response.content[0].text + f"[outputs]\n{results}[/outputs]" + f"[info]\n{additional_info}[/info]"}]
        })
        self.save_history()
        return "\n\n".join(results)

    def execute_single_action(self, action: str, details: Dict[str, str]) -> str:
        try:
            if action == "bash":
                command = details['content'].strip()
                logger.info(f"Executing bash command: {command}")
                result = run_bash_command(command)
                print(result)
                return result

            elif action == "modify":
                file_path = details['file_path']
                content = details['content']
                logger.info(f"Modifying file: {file_path}")
                modify_file(file_path, content)
                print(f"\nModified file: {file_path}")
                return f'{file_path} modified'

            elif action == "analyze":
                analysis = details['content']
                logger.info("Providing code analysis")
                print(f"\nAnalysis:\n{analysis}")
                return analysis

            elif action == "info":
                info = details['content']
                logger.info("Providing information")
                print(f"\nInformation:\n{info}")
                return info

        except Exception as e:
            error_msg = f"An error occurred during {action}: {str(e)}"
            logger.error(error_msg)
            print(f"\n{error_msg}")
            return error_msg

    def load_file_content(self, file_path: str) -> str:
        try:
            with open(file_path, 'r') as file:
                content = file.read()

            if self.conversation_history and self.conversation_history[-1]["role"] == "user":
                self.conversation_history[-1]["content"][0]["text"] += f"\nContent of file {file_path}:\n\n{content}"
            else:
                self.conversation_history.append({
                    "role": "user",
                    "content": [{"type": "text", "text": f"Content of file {file_path}:\n\n{content}"}]
                })

            self.save_history()
            return f"File content loaded: {file_path}"
        except FileNotFoundError:
            return f"File not found: {file_path}"
        except PermissionError:
            return f"Permission denied: {file_path}"
        except Exception as e:
            return f"Error loading file: {str(e)}"

def main():
    models = {
        'claudeSonnet-3.5': 'claude-3-5-sonnet-20240620',
        'claudeOpus-3': 'anthropic.claude-3-opus-20240229',
        'claudeSonnet-3': 'anthropic.claude-3-sonnet-20240229',
        'claudeHaiku-3': 'claude-3-haiku-20240307'
    }

    assistant = AIAssistant(model_id=models["claudeSonnet-3.5"])

    logger.info("AI Assistant initialized")

    print("Welcome to the AI Assistant. Type 'exit' to quit, 'help' for commands, or any bash command to execute directly.")

    while True:
        user_input = assistant.session.prompt(assistant.get_prompt(), style=assistant.style).strip()

        if user_input.lower() in ['exit', 'quit', 'bye', 'q']:
            logger.info("Exiting AI Assistant")
            break

        if user_input.lower() == 'help':
            print_help()
            continue

        if user_input.startswith('cd ') or user_input.startswith('load_file '):
            result = assistant.process_user_input(user_input)
            print(result)
        else:
            try:
                result = subprocess.run(user_input, shell=True, check=True, text=True, capture_output=True)
                print(result.stdout)
                if result.stderr:
                    print("Errors:", result.stderr)
            except subprocess.CalledProcessError as e:
                response = assistant.process_user_input(user_input)

def print_help():
    help_text = """
    Available commands:
    - exit, quit, bye, q: Exit the AI Assistant
    - load_file <file_path>: Load the content of a file into the conversation history
    - help: Display this help message
    - Any bash command: Execute the command directly
    - Any other input: Process with the AI Assistant
    """
    print(help_text)

if __name__ == "__main__":
    main()

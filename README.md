### AI Assistant Tool

This tool is an AI-powered assistant designed to help with code analysis, modification, and optimization. It primarily focuses on Python code but can also execute bash commands, modify files, commit changes to Git, and run/test Python code.

#### Features:

- Code Analysis: Provide insights and suggestions for improving code quality, efficiency, and readability.\n- Code Modification: Modify the contents of existing files within the current directory or its subdirectories.

- Bash Command Execution: Execute a limited set of allowed bash commands for file operations and code testing.

- Git Integration: Commit changes to a Git repository, creating a new branch for each modification.

- Python Code Testing: Run and test Python code after making modifications.

#### Usage:

- Ensure you have the required dependencies installed (Python, Git, and the necessary Python packages).

- Set the OPENAI_API_KEY environment variable with your OpenAI API key.

- Run the `ai_assistant.py` script.

- Interact with the AI assistant by providing input in the specified format:

  - For executing bash commands: <command>
  
  - For use the model you'll need only write the message in the prompt

- The AI assistant will process your input, perform the requested action, and provide a response.

- If modifications are made, the changes will be committed to a new Git branch with a descriptive commit message.

- For Python code testing, provide the path to the main file when prompted.

##### Note: This tool has certain limitations and rules, such as only working with existing files (except for creating new files or directories), staying within the current directory or its subdirectories, and using only a limited set of allowed bash commands. This was created using it.

Contributions and improvements are welcome! Feel free to fork the repository and submit pull requests.
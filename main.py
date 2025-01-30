from langchain_core.tools import Tool
from langchain_community.llms import Ollama
from langchain.agents import create_react_agent
from langchain.agents import AgentExecutor
from langchain_core.prompts import PromptTemplate
from typing import Dict, Any
import git
import os
import json

class GitTools:
    def __init__(self, repo_path: str):
        self.repo_path = repo_path
        self.repo = git.Repo(repo_path)

    def read_file(self, file_path: str) -> Dict[str, Any]:
        """Read content from a file in the repository"""
        try:
            full_path = os.path.join(self.repo_path, file_path)
            if not os.path.exists(full_path):
                return {
                    "status": "error",
                    "message": f"File {file_path} does not exist"
                }
            
            with open(full_path, 'r') as f:
                content = f.read()
            
            return {
                "status": "success",
                "content": content,
                "message": f"File {file_path} was read successfully"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }

    def modify_file(self, file_path: str, content: str) -> Dict[str, Any]:
        """Modify or create a file in the repository"""
        try:
            full_path = os.path.join(self.repo_path, file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            with open(full_path, 'w') as f:
                f.write(content)
            
            return {
                "status": "success",
                "message": f"File {file_path} has been modified"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }

    def commit_changes(self, message: str) -> Dict[str, Any]:
        """Commit changes to the repository"""
        try:
            # Add all changes
            self.repo.git.add(A=True)
            
            # Commit changes
            self.repo.index.commit(message)
            
            return {
                "status": "success",
                "message": f"Changes committed with message: {message}"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }

class GitAssistant:
    def __init__(self, repo_path: str, model_name: str = "codellama"):
        self.git_tools = GitTools(repo_path)
        self.llm = Ollama(model=model_name, temperature=0)
        
        # Define tools
        self.tools = [
            Tool(
                name="read_file",
                description="""Read content from a file in the repository.
                Argument must be provided as a JSON string with a 'file_path' key.
                Example: {"file_path": "example.py"}""",
                func=lambda x: self.git_tools.read_file(**json.loads(x))
            ),
            Tool(
                name="modify_file",
                description="""Modify or create a file in the git repository. 
                Arguments must be provided as a JSON string with 'file_path' and 'content' keys.
                Example: {"file_path": "example.py", "content": "print('hello')"}""",
                func=lambda x: self.git_tools.modify_file(**json.loads(x))
            ),
            Tool(
                name="commit_changes",
                description="""Commit all changes in the repository. 
                Argument must be provided as a JSON string with a 'message' key.
                Example: {"message": "Add new file"}""",
                func=lambda x: self.git_tools.commit_changes(**json.loads(x))
            )
        ]

        # Create ReAct prompt template
        template = """You are a helpful AI assistant that helps users with Git repository operations.

Tools available:
{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: must be a valid JSON string with the required arguments
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know what to do
Final Answer: the final answer to the original input question

When using read_file, provide argument as: {{"file_path": "path/to/file"}}
When using modify_file, provide arguments as: {{"file_path": "path/to/file", "content": "file content"}}
When using commit_changes, provide argument as: {{"message": "commit message"}}

For code refactoring tasks:
1. First read the existing file content
2. Analyze the code and plan the refactoring
3. Write the refactored code
4. Modify the file with the new code
5. Commit the changes with a descriptive message

Begin!

Question: {input}
{agent_scratchpad}"""

        prompt = PromptTemplate.from_template(template)

        # Create ReAct agent
        self.agent = create_react_agent(self.llm, self.tools, prompt)
        self.agent_executor = AgentExecutor(agent=self.agent, tools=self.tools, verbose=True, handle_parsing_errors=True)

    def process_message(self, user_input: str) -> str:
        """Process user input and return the response"""
        try:
            response = self.agent_executor.invoke({"input": user_input})
            return response["output"]
        except Exception as e:
            return f"Error occurred: {str(e)}\nTip: Make sure Ollama is running with the codellama model"

def main():
    # Initialize the assistant with the current directory as the repo
    try:
        assistant = GitAssistant(os.getcwd())
        
        print("Git Assistant using LangChain and Ollama")
        print("----------------------------------------")
        print("Using codellama model by default. Make sure Ollama is running!")
        print("Type 'exit' to quit")
        
        while True:
            user_input = input("\nYou: ")
            
            if user_input.lower() == 'exit':
                break
                
            response = assistant.process_message(user_input)
            print(f"\nAssistant: {response}")
    except git.exc.InvalidGitRepositoryError:
        print("Error: Current directory is not a Git repository. Please run this script inside a Git repository.")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()

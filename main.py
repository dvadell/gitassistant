from langchain_core.tools import Tool
from langchain_community.llms import Ollama
from langchain.agents import create_openai_tools_agent
from langchain.agents import AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import LLMChain
from typing import Dict, Any
import git
import os

class GitTools:
    def __init__(self, repo_path: str):
        self.repo_path = repo_path
        self.repo = git.Repo(repo_path)

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
        self.llm = Ollama(model=model_name)
        
        # Define tools
        self.tools = [
            Tool(
                name="modify_file",
                description="Modify or create a file in the git repository. Use this when you need to create or update file content.",
                func=self.git_tools.modify_file
            ),
            Tool(
                name="commit_changes",
                description="Commit all changes in the repository. Use this after modifying files to save the changes.",
                func=self.git_tools.commit_changes
            )
        ]

        # Create agent prompt with agent_scratchpad
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a helpful AI assistant that helps users with Git repository operations.
            You can modify files and commit changes using the provided tools.
            Always think step by step about what needs to be done, and use the appropriate tools when needed.
            If you're modifying files, make sure to commit the changes afterwards."""),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])

        # Create agent
        self.agent = create_openai_tools_agent(self.llm, self.tools, prompt)
        self.agent_executor = AgentExecutor(agent=self.agent, tools=self.tools, verbose=True)

    def process_message(self, user_input: str) -> str:
        """Process user input and return the response"""
        try:
            response = self.agent_executor.invoke({"input": user_input})
            return response["output"]
        except Exception as e:
            return f"Error occurred: {str(e)}"

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

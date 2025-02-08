# Installation
```
pip install langchain langchain-community gitpython
```

# Running gitassistant
## Requirements
1. Install ollama ( https://ollama.com/ ) with some models (`codellama`, `qwen2.5-coder`).

2. Create a new project, or go to your project's git root.
```
$ mkdir new_project
$ cd new_project
$ git init
```
## Running
1. Run the program
```
$ gitassistant 
Git Assistant using LangChain and Ollama
----------------------------------------
Using qwen2.5-coder model by default. Make sure Ollama is running!
Type 'exit' to quit

You:
```

2. Tell it what you want it to do. For example:
```
You: Create a new file called get_temp.py that prints the temperature for the city of Buenos Aires, Argentina. Add debugging print statements to see the response from the API. Commit the file.
```
3. Wait until you get the `You:` prompt again. You should have a new commit and a new `get_temp.py` file in your new project.

## Does it really work?
Sometimes. It depends on the model you can run. Most models I've tried on my laptop are too small to use the tools right. It should work better with bigger models.

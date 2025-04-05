import json

# Load the JSON file
with open('.devcontainer/devcontainer.json', 'r') as file:
    data = json.load(file)

# Print the loaded JSON data
print(data)
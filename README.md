# Execute python script to generate metadata

- python scripts/dulls_metadata.py
- "build/json" directory will be made and put by json metadata files.

# Execute python script to generate model

- blender dulls-parts -P scripts/dulls_model.py --background
- blender command is an alias of blender application command.
- --background option is not to run blender UI.
- Should keep the order of commnad arguments.
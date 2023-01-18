# Execute python script to generate metadata

```console
foo@bar:~$ python scripts/dulls_metadata.py
```

- "build/json" directory will be made and put by json metadata files.

# Execute python script to generate model

```console
foo@bar:~$ blender -P scripts/model.py dulls-parts 1 10 --background
```

- blender command is an alias of blender application command.
- 1 means start token id.
- 10 means end token id.
- --background option is not to run blender UI.
- Should keep the order of commnad arguments.

# How to alias blender command in mac

- https://docs.blender.org/manual/en/latest/advanced/command_line/launch/macos.html
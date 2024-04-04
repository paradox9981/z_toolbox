path = cmds.internalVar(usd=True)
script_path = f"{path}/z_toolbox/ziva_UI_auto_v2.py"  # Replace this with the actual path to your Python script
# Read the content of the script file
with open(script_path, 'r') as file:
    script_content = file.read()

# Execute the script using the exec function
exec(script_content)

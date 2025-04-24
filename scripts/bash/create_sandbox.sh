#!/bin/bash
# Create or refresh sandbox using the Salesforce CLI
# Requires $SANDBOX set in environment and jq installed

COMMAND_OUTPUT_FILE="sandboxes.json"
SANDBOX_DEF_FILE="config/sandbox-def.json"

# Convert comma-separated DO_NOT_REFRESH into an array
IFS=',' read -ra BLOCKED <<< "$DO_NOT_REFRESH"

# Check if SANDBOX is in the DO_NOT_REFRESH list
for name in "${BLOCKED[@]}"; do
  if [[ "$name" == "$SANDBOX" ]]; then
    echo "❌ Sandbox '$SANDBOX' is in the DO_NOT_REFRESH list. Cancelling pipeline."
    exit 1
  fi
done

# Append sandbox name to the sandbox-def.json (changes will be only kept in this current pipeline)
tmpfile=$(mktemp)
jq --arg name "$SANDBOX" '. + {sandboxName: $name}' "$SANDBOX_DEF_FILE" > "$tmpfile" && mv "$tmpfile" "$SANDBOX_DEF_FILE"

# Run the Salesforce CLI command and output to a file
sf data query --query "SELECT SandboxName FROM SandboxInfo" -t --json > "$COMMAND_OUTPUT_FILE"

# Parse the output file
FOUND=$(jq -r --arg name "$SANDBOX" '.result.records[]?.SandboxName | select(. == $name)' "$COMMAND_OUTPUT_FILE")

if [ -n "$FOUND" ]; then
  echo "Sandbox '$SANDBOX' exists in the org. Refreshing existing sandbox..."
  # ignore error to confirm if its exit code 68
  sf org refresh sandbox -f "config/sandbox-def.json" --async --no-prompt || EXIT_CODE=$?
else
  echo "Sandbox '$SANDBOX' not found in the org. Creating a new sandbox named '$SANDBOX'."
  # ignore error to confirm if its exit code 68
  sf org create sandbox -f "config/sandbox-def.json" --async --no-prompt || EXIT_CODE=$?
fi

# salesforce cli hardcodes exit code 68 for --async jobs
if [ "$EXIT_CODE" -eq 68 ]; then
  echo "Sandbox refresh request submitted successfully to Salesforce. Please monitor your email to see when sandbox is ready..."
  exit 0
elif [ "$EXIT_CODE" -ne 0 ]; then
  echo "❌ Salesforce CLI returned unexpected error code $EXIT_CODE"
  exit 1
fi

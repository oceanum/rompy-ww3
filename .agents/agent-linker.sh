#!/bin/bash
# agent-linker.sh - Script to manage linking active agent configuration files

# Load configuration
CONFIG_FILE="./.agents/agents.json"
ACTIVE_AGENT=$(jq -r '.active_agent' "$CONFIG_FILE" 2>/dev/null)

if [ "$ACTIVE_AGENT" = "null" ] || [ -z "$ACTIVE_AGENT" ]; then
    echo "Error: Could not determine active agent from $CONFIG_FILE"
    exit 1
fi

AGENT_CONFIG=$(jq -r ".configurations[\"$ACTIVE_AGENT\"]" "$CONFIG_FILE" 2>/dev/null)

if [ "$AGENT_CONFIG" = "null" ]; then
    echo "Error: Configuration for agent '$ACTIVE_AGENT' not found"
    exit 1
fi

CONTEXT_FILE=$(echo "$AGENT_CONFIG" | jq -r '.context_file')
TARGET_LINK=$(echo "$AGENT_CONFIG" | jq -r '.target_link')
DESCRIPTION=$(echo "$AGENT_CONFIG" | jq -r '.description')

echo "Activating agent configuration: $ACTIVE_AGENT"
echo "Description: $DESCRIPTION"
echo "Source: $CONTEXT_FILE"
echo "Target: $TARGET_LINK"

# Remove existing link if it exists
if [ -L "$TARGET_LINK" ]; then
    rm "$TARGET_LINK"
    echo "Removed existing link: $TARGET_LINK"
fi

# Create new symbolic link
ln -s "$CONTEXT_FILE" "$TARGET_LINK"
echo "Created new link: $TARGET_LINK -> $CONTEXT_FILE"

echo "Agent configuration activated successfully!"
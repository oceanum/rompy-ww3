# LLM Agent Configurations

This directory contains configuration files for various LLM agents that can work with this repository. Each agent has its own subdirectory containing its specific context, tools, and configuration files.

## Structure

```
.agents/
├── README.md          # This file
├── qwen/              # Qwen agent configuration
│   ├── QWEN.md        # Context file for Qwen
│   └── config.json    # Optional configuration
├── cursor/            # Cursor IDE configuration
│   ├── context.md     # Context file for Cursor
│   └── settings.json  # Optional settings
├── claude/            # Claude Desktop configuration
│   ├── claude_ctx.md  # Claude context
│   └── tools.json     # Available tools
└── agents.json        # Agent selection/configuration file
```

## How it works

1. Each subdirectory contains the configuration files specific to an LLM agent
2. The `agents.json` file specifies which agent configuration should be activated
3. Git hooks are used to create symbolic links to the active agent's configuration

## Available Agents

- **qwen**: Configuration for Qwen Code
- **cursor**: Configuration for Cursor IDE
- **claude**: Configuration for Claude Desktop
- **copilot**: Configuration for GitHub Copilot Chat

## Setup

To configure which agent to use, edit the `agents.json` file:

```json
{
  "active_agent": "qwen",
  "configurations": {
    "qwen": {
      "context_file": "./.agents/qwen/QWEN.md",
      "target_link": "./QWEN.md"
    },
    "cursor": {
      "context_file": "./.agents/cursor/context.md", 
      "target_link": "./cursor_context.md"
    }
  }
}
```

## Git Hook Integration

A pre-commit hook can be configured to automatically link the active agent's context file to the project root when working with specific agents.
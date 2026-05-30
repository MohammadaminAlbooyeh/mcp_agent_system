# MCP Protocol Guide

## What is MCP?

Model Context Protocol (MCP) is a standardized protocol for communication between AI agents and tools/resources.

## How It Works

1. Agent connects to MCP Server
2. Agent lists available tools
3. Agent calls tools with parameters
4. Server executes tools and returns results
5. Agent can also fetch resources and prompts

## Protocol Flow

```
Client          MCP Server
  |                  |
  |-- list_tools -->|
  |<-- tools list --|
  |                  |
  |-- call_tool ---->|
  |<-- tool result --|
  |                  |
  |-- get_resource ->|
  |<-- resource data-|
```

## MCP in This Project

The MCP Server exposes:
- **22 tools** across 7 categories
- **5 resources** for data access
- **4 prompt templates** for agent behavior

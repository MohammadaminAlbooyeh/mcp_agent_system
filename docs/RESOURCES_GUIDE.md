# Resources Guide

## Available Resources

### Database Schema
- URI: `database://schema`
- Provides current database schema information

### File System
- URI: `file://system`
- Provides current directory contents

### API Endpoints
- URI: `api://endpoints`
- Lists available REST API endpoints

### Memory State
- URI: `memory://state`
- Shows current agent memory state

## Usage

Resources can be fetched via MCP protocol:
```python
resource_data = await client.get_resource("database://schema")
```

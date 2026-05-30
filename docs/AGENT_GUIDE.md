# Agent Guide

## Core Architecture

The agent follows a modular architecture:

- **Agent**: Main entry point, coordinates all components
- **Planner**: Creates step-by-step plans
- **Executor**: Executes planned steps using tools
- **Evaluator**: Evaluates results
- **Memory**: Manages short-term and long-term memory
- **Reasoning**: Chain-of-thought and ReAct patterns
- **LLM**: Multiple LLM provider support

## Reasoning Patterns

### Chain of Thought
Breaks down complex tasks into step-by-step reasoning.

### ReAct Pattern
Alternates between reasoning (Thought) and acting (Action/Observation).

### Self-Reflection
Reviews and corrects its own outputs.

## Memory

- **Short-term**: Current task context
- **Long-term**: Persistent knowledge storage
- **Conversation**: Message history
- **Context Window**: Token-aware context management

# Setup Guide for New Features

This guide covers setup and usage of the new features added to the MCP Agent System.

## 1. Session Management Setup

### Enable Sessions in Agent
```python
from agent.core.agent import Agent
from agent.core.session_manager import SessionManager
from backend.services.session_repository import SessionRepository

# Initialize session manager
session_manager = SessionManager(ttl_minutes=1440)
session_repository = SessionRepository()
session_manager.set_repository(session_repository)

# Create agent with session support
agent, session_id = await Agent.create_with_session(
    config={"llm": "openai"},
    session_manager=session_manager,
    user_id="user@example.com"
)

# Run task (automatically checkpoints state)
result = await agent.run("Find information about Python async")

# Later: Restore session
restored_agent = await Agent.restore_with_session(
    config={"llm": "openai"},
    session_id=session_id,
    session_manager=session_manager
)
```

### Database Migration
```bash
# Run this to create sessions table
python -c "from backend.models.database import init_db; init_db()"
```

### Environment Variables
```bash
# .env file
SESSION_TTL_MINUTES=1440
SESSION_MAX_ACTIVE=1000
SESSION_CLEANUP_INTERVAL=60
DATABASE_URL=postgresql://user:pass@localhost/mcp_agent_db
```

---

## 2. Semantic Memory Setup

### Enable Semantic Search
```python
from agent.memory.memory_manager import MemoryManager

# Option 1: Local embeddings (requires sentence-transformers)
memory = MemoryManager(
    use_semantic=True,
    embedding_provider="local",
    vector_store_type="faiss"
)

# Option 2: OpenAI embeddings (requires OpenAI API key)
memory = MemoryManager(
    use_semantic=True,
    embedding_provider="openai",
    vector_store_type="faiss"
)

# Store memory with embeddings
await memory.store("Python async guide", "async/await patterns in Python...", memory_type="long_term")

# Search using semantic similarity
results = await memory.semantic_search("async programming", top_k=5)
for key, value, score in results:
    print(f"{key}: {score:.2f}")

# Hybrid search (keyword + semantic)
results = await memory.search("asyncio", strategy="hybrid", limit=10)
```

### Dependencies
```bash
pip install sentence-transformers  # for local embeddings
pip install faiss-cpu              # for vector indexing
pip install openai                 # for OpenAI embeddings (optional)
```

### Environment Variables
```bash
# .env file
EMBEDDING_PROVIDER=local          # or "openai"
EMBEDDING_MODEL=all-MiniLM-L6-v2  # or "text-embedding-3-small"
OPENAI_API_KEY=sk-...             # if using OpenAI
VECTOR_STORE_BACKEND=faiss        # or "memory"
```

---

## 3. OAuth/Gmail Setup

### Prerequisites
1. Create Google Cloud project
2. Enable Gmail API
3. Create OAuth 2.0 credentials (type: Web application)
4. Add authorized redirect URIs

### Configuration
```bash
# .env file
GOOGLE_CLIENT_ID=xxx.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your_secret
GOOGLE_REDIRECT_URI=http://localhost:3000/oauth/callback
ENCRYPTION_KEY=<generate with: python -c "from backend.utils.encryption import EncryptionUtil; print(EncryptionUtil.generate_key())">
```

### Usage in Code
```python
from backend.services.gmail_oauth_service import GmailOAuthService
from backend.services.oauth_repository import OAuthRepository

oauth_repo = OAuthRepository()
gmail_oauth = GmailOAuthService(oauth_repo)

# Get authorization URL
auth_url = gmail_oauth.get_auth_url(session_id="session123")
# User visits auth_url and gets redirected with 'code' parameter

# Exchange code for token
success = await gmail_oauth.exchange_code_for_token(
    code="auth_code_from_callback",
    session_id="session123"
)

# Get authenticated credentials
creds = await gmail_oauth.get_gmail_credentials("session123")

# Token automatically refreshes when needed
# Check status
status = await gmail_oauth.get_auth_status("session123")
print(f"Authenticated: {status['authenticated']}, Email: {status['user_email']}")

# Disconnect
await gmail_oauth.disconnect_gmail("session123")
```

### Using with Gmail Tools
```python
# Tools now support session_id for OAuth
from mcp_server.tools.email_tools.gmail_sender import GmailSenderTool

tool = GmailSenderTool()
result = await tool.execute(
    to="recipient@example.com",
    subject="Hello",
    body="Test email",
    session_id="session123"  # NEW: Uses OAuth token from session
)
```

---

## 4. Web Search Enhancement

### Basic Usage
```python
from mcp_server.tools.web_tools.web_search import WebSearchTool

tool = WebSearchTool()

# Structured results (default)
results = await tool.execute(
    query="machine learning algorithms",
    num_results=10,
    result_format="structured"
)
# Returns JSON with SearchResult objects

# Text format
text_results = await tool.execute(
    query="python async",
    num_results=5,
    result_format="text"
)

# JSON format
json_results = await tool.execute(
    query="web search",
    num_results=10,
    result_format="json"
)
```

### Result Structure
```python
{
  "position": 1,
  "title": "Page Title",
  "url": "https://example.com",
  "domain": "example.com",
  "snippet": "Page snippet/description...",
  "favicon_url": "https://www.google.com/s2/favicons?domain=example.com",
  "source_type": "web"
}
```

### Caching
```python
# Caching is automatic, configured via:
# - TTL: 24 hours (configurable)
# - Max cache size: 500 entries
# - Auto-cleanup of expired entries

# Clear cache if needed
await tool.cache.clear()

# Check cache stats
stats = await tool.cache.size()
```

### Advanced Filtering
```python
from mcp_server.tools.web_tools.search_parser import SearchResultFilter

filter = SearchResultFilter()

# Deduplicate results
deduplicated = filter.deduplicate(results)

# Filter by domain
github_results = filter.filter_by_domain(results, ["github.com"])

# Rank by relevance to query
ranked = filter.rank_by_relevance(results, "python async")

# Remove ads/duplicates
clean = filter.filter_out_ads_and_duplicates(results)
```

---

## 5. Error Handling

### Using Comprehensive Errors
```python
from agent.utils.exceptions import *

# Specific error types for different scenarios
try:
    result = await web_search_tool.execute(query)
except ToolExecutionError as e:
    print(f"Tool failed: {e.message}")
    print(f"Retry policy: {e.retry_policy.max_retries} retries")
    if e.retry_policy:
        delay = e.retry_policy.get_delay(attempt=1)
        await asyncio.sleep(delay)

# LLM errors with automatic retry
try:
    response = await llm.complete(prompt)
except LLMRateLimitError as e:
    print(f"Rate limited, waiting...")
    delay = e.retry_policy.get_delay(attempt=0)
    await asyncio.sleep(delay)

# Session errors
try:
    session = await session_manager.get_session(session_id)
except SessionExpiredError as e:
    print(f"Session expired: {e.context}")

# Custom error handling
try:
    await operation()
except AgentException as e:
    error_dict = e.to_dict()
    # Send to error tracking service
    await error_tracker.log(error_dict)
```

### Error Severity Levels
```python
from agent.utils.exceptions import ErrorSeverity

# Use severity for alerting
if error.severity == ErrorSeverity.CRITICAL:
    # Send alert immediately
    await alerting_service.alert(error.message)

elif error.severity == ErrorSeverity.ERROR:
    # Log error and retry
    logger.error(error.message)

elif error.severity == ErrorSeverity.WARNING:
    # Log warning, may recover
    logger.warning(error.message)

elif error.severity == ErrorSeverity.INFO:
    # Informational
    logger.info(error.message)
```

---

## 6. Full Workflow Example

```python
import asyncio
from agent.core.agent import Agent
from agent.core.session_manager import SessionManager
from backend.services.session_repository import SessionRepository
from backend.services.gmail_oauth_service import GmailOAuthService
from backend.services.oauth_repository import OAuthRepository
from agent.utils.exceptions import SessionExpiredError, ToolExecutionError

async def main():
    # Initialize services
    session_manager = SessionManager()
    session_repository = SessionRepository()
    session_manager.set_repository(session_repository)
    
    oauth_repo = OAuthRepository()
    gmail_oauth = GmailOAuthService(oauth_repo)
    
    # Create session
    agent, session_id = await Agent.create_with_session(
        config={"llm": "openai"},
        session_manager=session_manager,
        user_id="user@example.com"
    )
    
    print(f"Created session: {session_id}")
    
    # Step 1: Setup Gmail OAuth
    auth_url = gmail_oauth.get_auth_url(session_id)
    print(f"Please authorize: {auth_url}")
    
    # In real app, user would click and get code
    code = input("Enter auth code: ")
    success = await gmail_oauth.exchange_code_for_token(code, session_id)
    
    if success:
        status = await gmail_oauth.get_auth_status(session_id)
        print(f"Gmail authenticated: {status['user_email']}")
    
    # Step 2: Run agent task with semantic memory
    try:
        result = await agent.run("Search for Python async best practices and summarize")
        print(f"Task result: {result}")
    except ToolExecutionError as e:
        print(f"Tool failed: {e.message}")
        if e.retry_policy:
            delay = e.retry_policy.get_delay(0)
            print(f"Retrying in {delay:.1f}s...")
            await asyncio.sleep(delay)
    
    # Step 3: Semantic search in memory
    memory_results = await agent.memory.semantic_search("async programming", top_k=3)
    print("Memory search results:")
    for key, value, score in memory_results:
        print(f"  {key}: {score:.2f}")
    
    # Step 4: List active sessions
    active_sessions = await session_manager.list_active_sessions(user_id="user@example.com")
    print(f"Active sessions: {len(active_sessions)}")
    
    # Step 5: Close session
    await session_manager.complete_session(session_id, result=result)
    print(f"Session {session_id} completed")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Troubleshooting

### Sessions not persisting
- Check DATABASE_URL is set and PostgreSQL is running
- Run `init_db()` to create tables
- Check logs for database errors

### Embeddings slow or failing
- Install sentence-transformers: `pip install sentence-transformers`
- For first run, models download automatically (~400MB)
- Use local embeddings in development, OpenAI in production

### OAuth token refresh failing
- Check ENCRYPTION_KEY is set (must be consistent)
- Verify Google OAuth credentials are correct
- Check token expiry in database

### Web search not caching
- Ensure InMemorySearchCache is initialized
- Check cache TTL configuration
- Clear cache if experiencing stale results

### Errors not retrying
- Check retry_policy is set on exception
- Implement exponential backoff manually if needed
- Monitor error rates in observability dashboards

---

## Performance Optimization Tips

### Memory Optimization
- Use local embeddings instead of OpenAI for < 1000 memories
- Switch to pgvector for production (>10k memories)
- Implement memory consolidation for old memories

### Search Optimization
- Cache search results for common queries
- Use result filtering to reduce LLM processing
- Implement result pagination

### OAuth Optimization
- Implement token refresh background task
- Monitor token expiry to proactive-refresh
- Cache user info lookups

### Session Optimization
- Implement automatic session cleanup cronjob
- Use Redis for session cache if >1000 concurrent sessions
- Archive old sessions to separate storage

---

## Security Best Practices

1. **Environment Variables**
   - Never commit .env to git
   - Use different keys for dev/prod
   - Rotate encryption keys periodically

2. **OAuth Tokens**
   - Always encrypt tokens at rest
   - Use HTTPS for redirect URIs
   - Implement rate limiting on callback endpoint

3. **Memory Data**
   - Sanitize user inputs before storing
   - Implement access controls per session
   - Regular backups of memory database

4. **Error Handling**
   - Don't expose sensitive data in error messages
   - Log errors securely (not to client)
   - Monitor error patterns for attacks

---

## Monitoring & Observability

```python
# Get system statistics
stats = {
    "sessions": {
        "active": len(await session_manager.list_active_sessions()),
        "total_created": (session count from DB),
    },
    "memory": agent.memory.get_statistics(),
    "search_cache": tool.cache.size(),
    "oauth_tokens": (count of active tokens from DB),
}

# Setup error tracking
from agent.utils.exceptions import AgentException

try:
    await operation()
except AgentException as e:
    # Send to Sentry/DataDog/etc
    error_tracker.capture_exception(e.to_dict())
```

---

## Quick Reference

| Feature | Config Var | Default | Notes |
|---------|-----------|---------|-------|
| Session TTL | SESSION_TTL_MINUTES | 1440 (24h) | Adjustable per session |
| Embeddings | EMBEDDING_PROVIDER | local | Options: local, openai |
| Vector Store | VECTOR_STORE_BACKEND | faiss | Options: faiss, memory |
| Search Cache | - | Enabled | 500 entries, 24h TTL |
| Encryption | ENCRYPTION_KEY | Generated | Use same key in all instances |
| OAuth | GOOGLE_* | Not set | Required for Gmail auth |

---

**For more details, see:**
- `COMPLETION_REPORT.md` - Full feature documentation
- `docs/API_REFERENCE.md` - API endpoint details
- `examples/` - Working example code

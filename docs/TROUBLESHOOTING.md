# Troubleshooting

## Common Issues

### MCP Server won't start
- Check Python version (3.11+)
- Verify dependencies: `pip install -r requirements.txt`
- Check port availability

### Agent not responding
- Check LLM API keys in `.env`
- Verify MCP server is running
- Check network connectivity

### Database errors
- Ensure PostgreSQL is running
- Check DATABASE_URL in `.env`
- Run `python scripts/init_db.py`

### Frontend not loading
- Check Node.js version (18+)
- Run `cd frontend && npm install`
- Check REACT_APP_API_URL

## Logs

Check application logs for detailed error information.

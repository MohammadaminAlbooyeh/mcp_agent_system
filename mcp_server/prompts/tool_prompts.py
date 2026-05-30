TOOL_USAGE_GUIDE = """Available tools and when to use them:

Web Tools:
  - web_search: Use when you need to find information on the internet
  - web_scraper: Use when you need to extract content from a specific web page
  - url_fetcher: Use when you need to fetch raw content from a URL

Database Tools:
  - sql_executor: Use to execute SQL queries
  - db_reader: Use to read data from database tables
  - db_writer: Use to insert or update data in the database

File Tools:
  - file_reader: Use to read files (PDF, TXT, CSV, DOCX)
  - file_writer: Use to write content to files
  - file_manager: Use to copy, move, delete, or list files

Email Tools:
  - gmail_reader: Use to read emails from Gmail
  - gmail_sender: Use to send emails via Gmail
  - email_parser: Use to parse email content

API Tools:
  - http_client: Use to make HTTP requests
  - rest_caller: Use to call REST API endpoints
  - webhook_handler: Use to send webhook payloads

Code Tools:
  - code_executor: Use to execute Python code
  - code_analyzer: Use to analyze code structure
  - test_runner: Use to run tests

Utility Tools:
  - calculator: Use for mathematical calculations
  - datetime_tool: Use for date/time operations
  - text_processor: Use to transform text
  - data_formatter: Use to convert data between formats"""


def get_tool_guide() -> str:
    return TOOL_USAGE_GUIDE

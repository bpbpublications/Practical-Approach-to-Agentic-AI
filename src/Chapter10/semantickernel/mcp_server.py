"""
This module implements a robust and efficient Model Context Protocol (MCP) server
for interacting with a PostgreSQL database. It is designed with best practices in
mind, including structured logging and clear configuration management.

The server provides a single tool, `execute_query`, which allows for the execution
of SQL queries against the connected database. The tool is designed to be flexible,
handling both data retrieval (SELECT) and data manipulation (INSERT, UPDATE, DELETE)
queries.

Key Features:
- **Structured Logging**: Utilizes Python's built-in logging module to provide
  detailed and structured logs, which are essential for debugging and monitoring in a
  production environment.
- **Configuration Management**: Centralizes all configuration parameters, such as
  database credentials and logging settings, making the server easy to configure and
  maintain.
- **Asynchronous Operations**: Built on top of an asynchronous framework, allowing for
  non-blocking I/O operations and improved scalability.
- **Error Handling**: Includes comprehensive error handling to gracefully manage
  database-related issues, ensuring the stability of the server.
- **Dynamic Query Execution**: The `execute_query` tool can execute arbitrary SQL
  queries, returning results in a JSON format that is easy to parse and use by
  client applications.

The server is intended to be run as a standalone process, typically managed by a
parent application that communicates with it over standard input/output. This design
allows for a clean separation of concerns and makes the server a reusable component
in a larger system.
"""

import json
import logging
import os
import sys
from dataclasses import dataclass

import psycopg2
from dotenv import load_dotenv
from mcp.server.fastmcp import Context, FastMCP
from psycopg2.extras import RealDictCursor

# Load environment variables from a .env file
load_dotenv()


# --- Configuration ---
@dataclass
class Settings:
    """Dataclass to hold all the configuration settings."""

    db_name: str = os.getenv("DB_NAME", "testdb")
    db_user: str = os.getenv("DB_USER", "user")
    db_password: str = os.getenv("DB_PASSWORD", "password")
    db_host: str = os.getenv("DB_HOST", "localhost")
    db_port: str = os.getenv("DB_PORT", "5432")
    log_level: str = os.getenv("LOG_LEVEL", "DEBUG").upper()


# --- Utility Functions ---
def setup_logging(log_level: str) -> logging.Logger:
    """
    Configures and returns a logger instance.

    Args:
        log_level: The desired logging level (e.g., 'INFO', 'DEBUG').

    Returns:
        A configured logger instance.
    """
    logger = logging.getLogger(__name__)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    logger.setLevel(log_level)
    return logger


# --- Global Variables ---
settings = Settings()
logger = setup_logging(settings.log_level)
mcp = FastMCP("PGSQLMCPServer")
db_conn: psycopg2.extensions.connection | None = None


# --- MCP Server Lifecycle Events ---
def connect_db(ctx: Context | None = None):
    """
    Establishes the database connection on server startup.
    This function is called once when the MCP server starts. It initializes the
    database connection using the settings provided. If the connection fails, it logs
    a critical error and exits, signaling the failure to the parent process.
    """
    global db_conn
    try:
        logger.info("Attempting to create database connection...")
        db_conn = psycopg2.connect(
            dbname=settings.db_name,
            user=settings.db_user,
            password=settings.db_password,
            host=settings.db_host,
            port=settings.db_port,
        )
        logger.info("✅ Database connection established successfully.")
        
    except psycopg2.Error as e:
        logger.critical(f"❌ Failed to establish database connection: {e}")
        sys.exit(1)


def close_db_connection(ctx: Context):
    """
    Closes the database connection on server shutdown.
    This function is called when the MCP server is shutting down. It ensures that
    the database connection is closed gracefully.
    """
    global db_conn
    if db_conn:
        db_conn.close()
        logger.info("✅ Database connection closed.")
    else:
        logger.warning("⚠️ No database connection to close.")
        


# --- MCP Tools ---
@mcp.tool()
async def execute_query(query: str, ctx: Context, params: dict | None = None) -> str:
    """
    Executes a SQL query and returns the result as a JSON string.

    This tool is the primary interface for interacting with the database. It uses
    the global database connection to execute the given query and returns the result.
    It handles different types of queries:
    - For SELECT queries, it returns a JSON array of objects.
    - For INSERT/UPDATE/DELETE queries, it commits the transaction and returns a
      success message with the number of affected rows.
    - In case of an error, it rolls back the transaction and returns a JSON object
      with an error message.

    Args:
        query: The SQL query to execute.
        ctx: The MCP context, used for logging.
        params: An optional dictionary of parameters to pass to the query.

    Returns:
        A JSON string representing the result of the query.
    """
    if not db_conn:
        logger.error("Database connection is not available.")
        return json.dumps({"error": "Database connection is not available."})

    try:
        with db_conn.cursor(cursor_factory=RealDictCursor) as cursor:
            logger.info(f"Executing query: {query} with params: {params}")
            await ctx.info(f"Executing query: {query} with params: {params}")

            cursor.execute(query, params)

            if cursor.description:
                res = cursor.fetchall()
                res_json = json.dumps(res, default=str)
                logger.info(f"Query result: {res_json}")
                await ctx.info(f"Query result: {res_json}")
                return res_json
            else:
                db_conn.commit()
                logger.info(
                    f"Query executed successfully. {cursor.rowcount} rows affected."
                )
                await ctx.info(
                    f"Query executed successfully. {cursor.rowcount} rows affected."
                )
                return json.dumps(
                    {"status": "success", "rows_affected": cursor.rowcount}
                )

    except psycopg2.Error as e:
        logger.error(f"❌ Query execution error: {e}")
        await ctx.error(f"❌ Query execution error: {e}")
        if db_conn:
            db_conn.rollback()
        return json.dumps({"error": str(e)})
    except Exception as e:
        logger.error(f"❌ An unexpected error occurred: {e}")
        await ctx.error(f"❌ An unexpected error occurred: {e}")
        if db_conn:
            db_conn.rollback()
        return json.dumps({"error": f"An unexpected error occurred: {e}"})


# --- Main Execution Block ---
if __name__ == "__main__":
    # The server is designed to be run as a subprocess by an MCP agent.
    # Running this script directly will start the server and listen for
    # commands over standard input/output.

    connect_db()

    logger.info("Starting MCP server...")
    mcp.run(transport="stdio")

#!/usr/bin/env python3
import os
import sys
import json
from pathlib import Path
from typing import Dict, Any, List

from dotenv import load_dotenv
from .mistral_ocr import MistralOCRProcessor
from mcp.server.fastmcp import FastMCP
from mcp.shared.exceptions import McpError
from mcp.types import (
    ErrorData,
    Tool,
    TextContent,
    PARSE_ERROR,
    INVALID_REQUEST,
    METHOD_NOT_FOUND,
    INVALID_PARAMS,
    INTERNAL_ERROR
)

# Load environment variables
load_dotenv()

# Environment validation
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
OCR_DIR = os.getenv("OCR_DIR")

if not MISTRAL_API_KEY:
    raise ValueError("MISTRAL_API_KEY environment variable is required")

if not OCR_DIR:
    raise ValueError("OCR_DIR environment variable is required")

# Inside container, OCR_DIR is always /data/ocr
OCR_DIR_PATH = Path("/data/ocr")

print(f"Using OCR directory: {OCR_DIR_PATH}", file=sys.stderr)

if not OCR_DIR_PATH.exists():
    print(f"Creating OCR directory: {OCR_DIR_PATH}", file=sys.stderr)
    OCR_DIR_PATH.mkdir(parents=True, exist_ok=True)

# Ensure output directory exists
OUTPUT_DIR = OCR_DIR_PATH / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

app = FastMCP("mcp-mistral-ocr")

ocr_processor = MistralOCRProcessor(api_key=MISTRAL_API_KEY)

@app.tool("list_tools")
async def list_tools() -> List[Tool]:
    """List available tools"""
    return [
        Tool(
            name="process_local_file",
            description="Process a file from the OCR_DIR directory",
            inputSchema={
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "Name of the file to process",
                    }
                },
                "required": ["filename"],
            }
        ),
        Tool(
            name="process_url_file",
            description="Process a file from a URL (max 50MB, 1000 pages)",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "URL of the file to process",
                    },
                    "file_type": {
                        "type": "string",
                        "description": "Type of file: 'image' or 'pdf'",
                        "enum": ["image", "pdf"]
                    }
                },
                "required": ["url", "file_type"],
            }
        )
    ]

@app.tool("process_local_file")
async def process_local_file(arguments: Dict[str, Any]) -> List[TextContent]:
    """Process a local file from OCR_DIR"""
    filename = arguments.get("filename")
    if not filename:
        raise McpError(ErrorData(
            code=INVALID_PARAMS,
            message="filename is required"
        ))
    
    file_path = OCR_DIR_PATH / filename
    if not file_path.exists():
        raise McpError(ErrorData(
            code=INVALID_PARAMS,
            message=f"File not found: {filename}"
        ))
    
    try:
        result = await ocr_processor.process_local_file(file_path, OUTPUT_DIR)
        return [TextContent(type="text", text=result)]
    except Exception as e:
        raise McpError(ErrorData(
            code=INTERNAL_ERROR,
            message=f"Error processing file: {str(e)}"
        ))

@app.tool("process_url_file")
async def process_url_file(arguments: Dict[str, Any]) -> List[TextContent]:
    """Process a file from a URL"""
    url = arguments.get("url")
    file_type = arguments.get("file_type")
    
    if not url:
        raise McpError(ErrorData(
            code=INVALID_PARAMS,
            message="url is required"
        ))
    
    if not file_type:
        raise McpError(ErrorData(
            code=INVALID_PARAMS,
            message="file_type is required"
        ))
    
    if file_type not in ["image", "pdf"]:
        raise McpError(ErrorData(
            code=INVALID_PARAMS,
            message="file_type must be either 'image' or 'pdf'"
        ))
    
    try:
        result = await ocr_processor.process_url_file(url, file_type, OUTPUT_DIR)
        return [TextContent(type="text", text=result)]
    except Exception as e:
        raise McpError(ErrorData(
            code=INTERNAL_ERROR,
            message=f"Error processing URL: {str(e)}"
        ))

if __name__ == "__main__":
    app.run(transport='stdio')

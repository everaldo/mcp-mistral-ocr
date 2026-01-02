# MCP Mistral OCR
[![smithery badge](https://smithery.ai/badge/@everaldo/mcp-mistral-ocr)](https://smithery.ai/server/@everaldo/mcp-mistral-ocr)

An MCP server that provides OCR capabilities using Mistral AI's OCR API. This server can process both local files and URLs, supporting images and PDFs.

## Features

- Process local files (images and PDFs) using Mistral's OCR
- Process files from URLs with explicit file type specification
- Support for multiple file formats (JPG, PNG, PDF, etc.)
- Results saved as JSON files with timestamps
- Docker containerization
- UV package management

## Environment Variables

- `MISTRAL_API_KEY`: Your Mistral AI API key
- `OCR_DIR`: Directory path for local file processing. Inside the container, this is always mapped to `/data/ocr`

## Installation

### Installing via Smithery

To install Mistral OCR for Claude Desktop automatically via [Smithery](https://smithery.ai/server/@everaldo/mcp-mistral-ocr):

```bash
npx -y @smithery/cli install @everaldo/mcp/mistral-crosswalk --client claude
```

### Using Docker

1. Build the Docker image:
```bash
docker build -t mcp-mistral-ocr .
```

2. Run the container:
```bash
docker run -e MISTRAL_API_KEY=your_api_key -e OCR_DIR=/data/ocr -v /path/to/local/files:/data/ocr mcp-mistral-ocr
```

### Local Development

1. Install UV package manager:
```bash
pip install uv
```

2. Create and activate virtual environment:
```bash
uv venv
source .venv/bin/activate  # On Unix
# or
.venv\Scripts\activate  # On Windows
```

3. Install dependencies:
```bash
uv pip install .
```

## Claude Desktop Configuration

Add this configuration to your claude_desktop_config.json:

```json
{
  "mcpServers": {
    "mistral-ocr": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-e",
        "MISTRAL_API_KEY",
        "-e",
        "OCR_DIR",
        "-v",
        "C:/path/to/your/files:/data/ocr",
        "mcp-mistral-ocr:latest"
      ],
      "env": {
        "MISTRAL_API_KEY": "<YOUR_MISTRAL_API_KEY>",
        "OCR_DIR": "C:/path/to/your/files"
      }
    }
  }
}
```

## Available Tools

### 1. process_local_file

Process a file from the configured OCR_DIR directory.

```json
{
    "name": "process_local_file",
    "arguments": {
        "filename": "document.pdf"
    }
}
```

### 2. process_url_file

Process a file from a URL. Requires explicit file type specification.

```json
{
    "name": "process_url_file",
    "arguments": {
        "url": "https://example.com/document",
        "file_type": "image"  // or "pdf"
    }
}
```

## Output

OCR results are saved in JSON format in the `output` directory inside `OCR_DIR`. Each result file is named using the following format:
- For local files: `{original_filename}_{timestamp}.json`
- For URLs: `{url_filename}_{timestamp}.json` or `url_document_{timestamp}.json` if no filename is found in the URL

The timestamp format is `YYYYMMDD_HHMMSS`.

## Supported File Types

- Images: JPG, JPEG, PNG, GIF, WebP
- Documents: PDF and other document formats supported by Mistral OCR

## Limitations

- Maximum file size: 50MB (enforced by Mistral API)
- Maximum document pages: 1000 (enforced by Mistral API)

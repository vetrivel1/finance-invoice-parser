# Finance Invoice Parser API

This project provides a FastAPI-based web service to parse PDF invoices, format the extracted text using a powerful Large Language Model (LLM), and return a structured CSV output.

## Features

- **PDF Parsing**: Extracts raw text content from uploaded PDF files.
- **LLM-Powered Formatting**: Leverages Azure's GPT-4o model to intelligently structure the raw text into a clean, predictable CSV format.
- **Simple API Endpoint**: Exposes a single endpoint for a seamless PDF-to-CSV workflow.
- **Easy to Deploy**: Runs as a standard FastAPI application using Uvicorn.

---

## Prerequisites

- Python 3.10+
- A virtual environment (recommended)
- An Azure OpenAI API key with access to a GPT-4o model deployment.

---

## Setup and Installation

1.  **Clone the repository (if you haven't already):**
    ```bash
    git clone https://github.com/vetrivel1/finance-invoice-parser.git
    cd finance-invoice-parser
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

---

## Running the Server

1.  **Set the required environment variable:**

    The API requires an Azure OpenAI API key. Export it in your terminal session before running the server.

    ```bash
    export AZURE_API_KEY="your_azure_openai_api_key_here"
    ```

2.  **Start the API server:**

    Run the application using Uvicorn. The `--reload` flag is useful for development as it automatically restarts the server when code changes are detected.

    ```bash
    uvicorn api_invoice_parser:app --reload
    ```

    The server will be running at `http://127.0.0.1:8000`.

---

## API Usage

The API provides one primary endpoint for processing invoices.

### POST `/format-invoice-csv/`

This endpoint accepts a PDF file upload and returns the formatted data as a raw CSV string in the response body.

#### Example Request with `curl`

To use the endpoint, send a `POST` request with the PDF file as multipart form data.

```bash
curl -X POST "http://127.0.0.1:8000/format-invoice-csv/" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@/path/to/your/invoice.pdf" \
     --output "formatted_invoice.csv"
```

-   Replace `/path/to/your/invoice.pdf` with the actual path to your invoice file.
-   The `--output` flag saves the raw CSV response directly into a file named `formatted_invoice.csv`.
-   If you are calling this from a script (e.g., Google Apps Script), the response body will contain the CSV data, which you can then parse and use as needed. 
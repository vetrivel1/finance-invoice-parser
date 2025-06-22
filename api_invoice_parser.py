import os
import tempfile
import csv
import io
import re
import litellm
import pandas as pd
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import Response
import pdfplumber
import uvicorn

app = FastAPI(
    title="Invoice Formatting API",
    description="API to parse a PDF invoice, format it using an LLM, and return a structured CSV file.",
    version="2.0.0"
)

# --- Helper Functions from invoice_format.py ---

def get_azure_openai_response(system_prompt, user_prompt):
    """
    Invokes the Azure OpenAI service with the provided system and user prompts.
    """
    api_key = os.environ.get("AZURE_API_KEY")
    if not api_key:
        raise ValueError("The AZURE_API_KEY environment variable is not set.")

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    try:
        print("Connecting to Azure OpenAI for processing...")
        response = litellm.completion(
            model="azure/vetri-gpt-4o",
            messages=messages,
            api_base="https://vetri-workspace.openai.azure.com/",
            api_version="2024-02-01",
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"An error occurred while communicating with Azure OpenAI: {e}")
        # Propagate error to be caught by the endpoint handler
        raise HTTPException(status_code=502, detail=f"LLM service call failed: {e}")

# --- PDF Parsing Function ---

def parse_pdf_to_text(pdf_file_path: str) -> str:
    """
    Extract text from a PDF file using pdfplumber.
    """
    full_text = ""
    try:
        with pdfplumber.open(pdf_file_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    full_text += text + "\n\n"
    except Exception as e:
        raise IOError(f"Error processing PDF file: {str(e)}")
    
    return full_text.strip()

# --- Main API Endpoint ---

@app.post("/format-invoice-csv/")
async def format_invoice_to_csv(file: UploadFile = File(...)):
    """
    Upload a PDF invoice, process it with an LLM, and return the 
    structured data as a downloadable CSV file.
    """
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    temp_pdf_path = None
    try:
        # 1. Read configuration files for the LLM
        try:
            with open('format.md', 'r', encoding='utf-8') as f:
                system_prompt = f.read()
            with open('mapping.md', 'r', encoding='utf-8') as f:
                mapping_data = f.read()
        except FileNotFoundError as e:
            raise HTTPException(status_code=500, detail=f"A required configuration file is missing: {e}")

        # 2. Save uploaded PDF to a temporary file for robust processing
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_pdf:
            temp_pdf.write(await file.read())
            temp_pdf_path = temp_pdf.name

        # 3. Extract raw text from the PDF
        try:
            raw_text = parse_pdf_to_text(temp_pdf_path)
        except IOError as e:
            raise HTTPException(status_code=500, detail=str(e))

        # 4. Construct the user prompt for the LLM
        user_prompt = f"""
I am processing the file `{file.filename}`.

Here is the full reference manual (`mapping.md`):
---
{mapping_data}
---

Here is the raw extracted text from the source PDF file `{file.filename}`:
---
{raw_text}
---

Your task is to follow the instructions from the system prompt. Specifically, use the filename `{file.filename}` to find the correct entry in the `mapping.md` data, extract the header information, and combine it with the line items from the source text provided above. Produce ONLY the CSV output for this single file, including the header row.
"""
        # 5. Get the formatted CSV from the LLM
        formatted_csv_str = get_azure_openai_response(system_prompt, user_prompt)

        if not formatted_csv_str:
            raise HTTPException(status_code=500, detail="LLM returned an empty response.")

        # 6. Clean the LLM response to ensure it's valid CSV
        cleaned_csv = re.sub(r'^```(csv)?\s*', '', formatted_csv_str, flags=re.IGNORECASE).strip()
        cleaned_csv = re.sub(r'```$', '', cleaned_csv).strip()

        if not cleaned_csv:
            raise HTTPException(status_code=500, detail="LLM response was empty after cleaning.")

        # 7. Return the CSV data directly in the response body
        return Response(
            content=cleaned_csv.encode('utf-8'),
            media_type='text/csv'
        )

    except Exception as e:
        # Catch-all for any other unexpected errors
        if isinstance(e, HTTPException):
            raise  # Re-raise HTTPException to preserve status code and detail
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

    finally:
        # 8. Ensure the temporary PDF file is always cleaned up
        if temp_pdf_path and os.path.exists(temp_pdf_path):
            os.unlink(temp_pdf_path)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 
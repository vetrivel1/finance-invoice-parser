### AI Prompt for Consolidating Invoice Data

**Task:** You are an advanced data processing agent. Your primary function is to consolidate invoice data from multiple CSV files into a single, master CSV file. You will use a reference markdown document to enrich the data from each source file.

**Inputs:**
1.  **Reference Manual:** `mapping.md` - This file contains detailed, human-readable information about each invoice, including supplier details, invoice numbers, dates, and tax information. You must use this as your primary source for non-line-item data.
2.  **Source Data Directory:** `output/` - This directory contains multiple CSV files. Each file represents the line-item details for a specific invoice.
3.  **Output Schema:** The final output must conform to the structure of `Data points.xlsx - Sheet1.csv`, which includes the following columns: `Bill no,Bill date,Vendor Name,Address,GSTN of vendor,Item Name,Qty,Rate,Amount,Discount,Net Amount,HSN code,GST name (%)`.

**Instructions:**

1.  **Initialize Output:** Begin by creating the header row for your final output file, `Data points.xlsx - Sheet1.csv`.

2.  **Iterate Through Source Files:** Process each `.csv` file located in the `output/` directory one by one. For each file, perform the following steps:

3.  **Identify and Map:**
    *   Use the **filename** of the input CSV (e.g., `Teceze inv-po#10325-1.csv`, `Edify Enterprises.csv`) to identify the corresponding supplier section in the `mapping.md` reference file (e.g., "Teceze Consultancy Services", "EDIFY ENTERPRISES").
    *   From the identified section in `mapping.md`, extract the following "header" details, which will be constant for all rows from this source file:
        *   **`Bill no`**: The `Invoice No` or `Invoice Number`.
        *   **`Bill date`**: The `Invoice Date` or `Dated`.
        *   **`Vendor Name`**: The `Supplier Name`.
        *   **`Address`**: The `Supplier Address`.
        *   **`GSTN of vendor`**: The `GSTIN` or `GST Number` of the supplier.

4.  **Process Line Items:**
    *   Open the source CSV file.
    *   For each row in the CSV (ignoring its header, if any), extract the line-item details.
    *   You will need to intelligently map the columns from the source CSV to the required output columns. The column names may not be exact matches. For example:
        *   **`Item Name`**: Map from a column like `Item Description`, `Description`, or similar.
        *   **`Qty`**: Map from `Quantity`, `Qty`, `Qty.`, etc.
        *   **`Rate`**: Map from `Rate`, `Price Per Unit`, etc.
        *   **`Amount` / `Net Amount`**: Map from `Amount`, `Total`, etc.
        *   **`HSN code`**: Map from `HSN/SAC`, `HSN Code`, etc.
    *   The `mapping.md` file can also be used to find the correct `HSN code` or `GST %` if it's not present in the line-item CSV.

5.  **Construct Output Rows:**
    *   For each line item processed, create a new row for the final CSV.
    *   This new row should be a combination of the **header details** (from `mapping.md`) and the **line-item details** (from the source CSV).
    *   Set the **`Discount`** column to `0` unless specified otherwise.
    *   Ensure all fields are populated according to the output schema.

6.  **Generate Final File:**
    *   Combine the rows generated from all the source CSV files.
    *   Save the complete, consolidated data into the `Data points.xlsx - Sheet1.csv` file, overwriting any existing content.

**Important Formatting Rules for CSV Output:**

1.  **Always Enclose Fields in Double Quotes:** Every field in the CSV output, including the headers, must be enclosed in double quotes. For example: `"Bill no","Bill date","Vendor Name",...`
2.  **Escape Internal Quotes:** If any data field contains a double quote (`"`) character, it must be escaped by prefixing it with another double quote. For example, a value like `12" screen` should be formatted as `"12"" screen"`.
3.  **Strict Adherence:** It is critical that you follow these CSV formatting rules strictly to ensure the output can be parsed correctly. Do not add any extra notes or text outside of the CSV data itself. 
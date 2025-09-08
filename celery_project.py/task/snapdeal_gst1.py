import pandas as pd
from task.workbook import ExcelWriter


class SnapdealGSTProcessor:
    def __init__(self, payload, sheet_name="Section 7(B)(2) in GSTR-1"):
        """
        payload: {
            "files": ["snapdeal_sales.xlsx"]
        }
        """
        files = payload.get("files", [])
        if not files or len(files) == 0:
            raise ValueError("Payload must contain at least one file (input Excel).")

        self.input_excel = files[0]
        self.sheet_name = sheet_name

    def process(self):
        df = pd.read_excel(self.input_excel, sheet_name=self.sheet_name)
        df.columns = df.columns.str.strip()  # Clean column names

        # Detect relevant columns
        delivered_col = next((col for col in df.columns if "Deliver" in col and "State" in col), None)
        taxable_col = next((col for col in df.columns if "Aggregate" in col and "Taxable" in col), None)

        if not delivered_col:
            raise KeyError("❌ No Delivered State column found in the sheet")
        if not taxable_col:
            raise KeyError("❌ No Aggregate Taxable Value column found in the sheet")

        # Group and summarize
        summary = df.groupby(delivered_col)[taxable_col].sum().reset_index()

        # Add required fields
        summary["Type"] = "OE"
        summary["Rate"] = 5
        summary["Applicable % of Tax Rate"] = ""
        summary["Cess Amount"] = 0
        summary["E-Commerce GSTIN"] = ""

        # Reorder and rename
        summary = summary[
            ["Type", delivered_col, "Applicable % of Tax Rate", "Rate", taxable_col, "Cess Amount", "E-Commerce GSTIN"]
        ]
        summary.rename(columns={delivered_col: "Place Of Supply", taxable_col: "Taxable Value"}, inplace=True)

        # Convert to list of dicts (JSON-ready)
        records = summary.to_dict(orient="records")
        return records


# ------------------ Handler Function ------------------
def snapdeal_handler(payload, output_file="snapdeal_b2cs.xlsx", sheet_name="B2CS Summary"):
    processor = SnapdealGSTProcessor(payload)
    data = processor.process()

    # Write to Excel
    excel_writer = ExcelWriter(output_file, sheet_name)
    excel_writer.write_data(data)
    excel_writer.save()

    return data

# ------------------ Manual Test ------------------
# if __name__ == "__main__":
#     payload = {
#         "files": [
#             r"C:\Users\st\Desktop\Rachit\GST_format\Snapdeal\input_files\snapdeal_sales.xlsx"
#         ]
#     }

#     processed_data = snapdeal_handler(payload)
#     print(processed_data[:5])  # Print first 5 records for verification
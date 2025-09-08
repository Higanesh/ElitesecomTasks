import pandas as pd
from task.workbook import ExcelWriter

class MeeshoGSTProcessor:
    def __init__(self, payload):
        """
        payload: {
            "files": ["excel_file.xlsx"]
        }
        """
        files = payload.get("files", [])
        if not files or len(files) == 0:
            raise ValueError("Payload must contain at least one file (Excel file).")
        self.excel_file = files[0]

    def find_taxable_col(self, df, df_name):
        for col in df.columns:
            if "Taxable" in col and "Value" in col:
                return col
        raise KeyError(f"No 'Taxable Value' column found in {df_name}")

    def process(self):
        # Load sheets
        sales_df = pd.read_excel(self.excel_file, sheet_name="Sales_Report")
        cashback_df = pd.read_excel(self.excel_file, sheet_name="Cash_Back_Report")

        # Detect taxable columns
        sales_taxable_col = self.find_taxable_col(sales_df, "Sales_Report")
        cashback_taxable_col = self.find_taxable_col(cashback_df, "Cash_Back_Report")

        # Process Sales Report
        if "Customer's Delivery State" not in sales_df.columns:
            raise KeyError("Sales_Report missing 'Customer's Delivery State' column")

        sales_summary = (
            sales_df.groupby("Customer's Delivery State")[sales_taxable_col]
            .sum()
            .reset_index()
        )
        sales_summary.rename(
            columns={"Customer's Delivery State": "State", sales_taxable_col: "Taxable Value"},
            inplace=True
        )
        sales_summary["Rate"] = 5

        # Process Cashback Report
        if "Customer's Delivery State" not in cashback_df.columns:
            raise KeyError("Cash_Back_Report missing 'Customer's Delivery State' column")

        cashback_summary = (
            cashback_df.groupby("Customer's Delivery State")[cashback_taxable_col]
            .sum()
            .reset_index()
        )
        cashback_summary.rename(
            columns={"Customer's Delivery State": "State", cashback_taxable_col: "Taxable Value"},
            inplace=True
        )
        cashback_summary["Rate"] = 5

        # Merge and summarize
        combined = pd.concat([sales_summary, cashback_summary], ignore_index=True)
        final_summary = combined.groupby(["State", "Rate"])["Taxable Value"].sum().reset_index()

        # Add fixed fields
        final_summary["Type"] = "OE"
        final_summary["Place Of Supply"] = final_summary["State"]
        final_summary["Applicable % of Tax Rate"] = ""
        final_summary["Cess Amount"] = 0
        final_summary["E-Commerce GSTIN"] = ""

        # Convert to list of dicts
        result = []
        for _, row in final_summary.iterrows():
            result.append({
                "Type": row["Type"],
                "Place Of Supply": row["Place Of Supply"],
                "Applicable % of Tax Rate": row["Applicable % of Tax Rate"],
                "Rate": row["Rate"],
                "Taxable Value": round(row["Taxable Value"], 2),
                "Cess Amount": row["Cess Amount"],
                "E-Commerce GSTIN": row["E-Commerce GSTIN"],
            })

        return result


# ------------------ Handler Function ------------------
def flipcart_handler(payload, output_file="summary.xlsx"):
    processor = MeeshoGSTProcessor(payload)
    processed_data = processor.process()

    # Write to Excel if ExcelWriter is implemented
    excel_writer = ExcelWriter(output_file, "GST Summary")
    excel_writer.write_data(processed_data)
    excel_writer.save()

    return processed_data


# # ------------------ Manual Test ------------------
# if __name__ == "__main__":
    # payload = {
    #     "files": [
    #         r"C:\Users\st\Desktop\Rachit\GST_format\Flipcart\input_files\sales_report.xlsx"
    #     ]
    # }

#     result = flipcart_handler(payload)
#     print("Processed Data:")
#     for row in result[:5]:  # print first 5 rows
#         print(row)
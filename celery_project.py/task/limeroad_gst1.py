import pandas as pd
from task.workbook import ExcelWriter

class LimeroadGSTProcessor:
    def __init__(self, payload, sheet_name="TCS_Summary"):
        """
        payload: {
            "files": ["input_excel.xlsx"]
        }
        """
        files = payload.get("files", [])
        if not files or len(files) == 0:
            raise ValueError("Payload must contain at least one file (input Excel).")

        self.input_excel = files[0]
        self.sheet_name = sheet_name

        # Mapping of state names to codes
        self.state_codes = {
            "andhra pradesh": "37-Andhra Pradesh",
            "bihar": "10-Bihar",
            "chhattisgarh": "22-Chhattisgarh",
            "dadra & nagar haveli": "26-Dadra & Nagar Haveli & Daman & Diu",
            "delhi": "07-Delhi",
            "gujarat": "24-Gujarat",
            "haryana": "06-Haryana",
            "karnataka": "29-Karnataka",
            "kerala": "32-Kerala",
            "madhya pradesh": "23-Madhya Pradesh",
            "maharashtra": "27-Maharashtra",
            "odisha": "21-Odisha",
            "punjab": "03-Punjab",
            "rajasthan": "08-Rajasthan",
            "sikkim": "11-Sikkim",
            "tamil nadu": "33-Tamil Nadu",
            "telangana": "36-Telangana",
            "uttar pradesh": "09-Uttar Pradesh",
            "uttarakhand": "05-Uttarakhand",
            "west bengal": "19-West Bengal"
        }

    def process(self):
        df = pd.read_excel(self.input_excel, sheet_name=self.sheet_name)
        df.columns = df.columns.str.strip()  # Clean column names

        records = []
        for _, row in df.iterrows():
            state = str(row["Customer State"]).strip().lower()
            place_of_supply = self.state_codes.get(state, state.title())
            records.append({
                "Type": "OE",
                "Place Of Supply": place_of_supply,
                "Applicable % of Tax Rate": "",
                "Rate": row.get("Total GST Rate", 0),
                "Taxable Value": round(row.get("Net Taxable Amount", 0), 2),
                "Cess Amount": 0,
                "E-Commerce GSTIN": ""
            })

        return records


# ------------------ Handler Function ------------------
def limeroad_handler(payload, output_file="b2cs_summary.xlsx", sheet_name="B2CS Summary"):
    processor = LimeroadGSTProcessor(payload, sheet_name="TCS_Summary")
    data = processor.process()

    # Write to Excel if ExcelWriter is available
    excel_writer = ExcelWriter(output_file, sheet_name)
    excel_writer.write_data(data)
    excel_writer.save()

    return data  # Return the processed data


# ------------------ Manual Test ------------------
if __name__ == "__main__":
    payload = {
        "files": [
            r"C:\Users\st\Desktop\Rachit\GST_format\Limeroad\input_files\limeroad_report.xlsx"
        ]
    }

    processed_data = limeroad_handler(payload)
    print(processed_data[:5])  # Print first 5 records for verification
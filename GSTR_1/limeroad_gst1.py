import pandas as pd
from logger_manager import LoggerManager
from workbook import ExcelWriter

class LimeroadGSTProcessor:
    def __init__(self, input_excel, sheet_name="TCS_Summary", log_file="limeroad_gst.log"):
        self.input_excel = input_excel
        self.sheet_name = sheet_name
        self.logger = LoggerManager.get_logger(log_file)

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

        self.logger.info(f"Loaded {self.sheet_name} with {len(df)} rows")

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

# ------------------ Manual Test ------------------
if __name__ == "__main__":
    input_file = r"C:\Users\st\Desktop\Rachit\GST_format\Limeroad\input_files\limeroad_report.xlsx"
    output_file = r"C:\Users\st\Desktop\Rachit\GST_format\Limeroad\input_files\final.xlsx"

    processor = LimeroadGSTProcessor(input_file)

    try:
        data = processor.process()

        # Write to Excel
        excel_writer = ExcelWriter(output_file, "B2CS Summary")
        excel_writer.write_data(data)
        excel_writer.save()

    except Exception as e:
        processor.logger.error(f"Error during processing: {e}")
        raise

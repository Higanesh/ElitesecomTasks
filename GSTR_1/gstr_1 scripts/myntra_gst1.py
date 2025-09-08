import os
import pandas as pd
from logger_manager import LoggerManager
from workbook import ExcelWriter
from validate_payload import validate_payload

# # ✅ Required files for Myntra only
# MYNTRA_REQUIRED_FILES = ["packed", "rt", "rto"]

# # ---------- Payload Validation (Myntra Only) ----------
# def validate_myntra_payload(payload):
#     """
#     Validate payload for Myntra marketplace.
#     payload = {
#         "marketplace_name": "myntra",
#         "files": ["path/to/packed.csv", "path/to/rt.csv", "path/to/rto.csv"],
#         "user_email": "user@example.com"
#     }
#     """
#     marketplace = payload.get("marketplace_name", "").lower()
#     files = payload.get("files", [])
#     user_email = payload.get("user_email", "unknown")

#     # 1. Check if the marketplace is Myntra
#     if marketplace != "myntra":
#         return False, f"❌ Invalid marketplace selected by {user_email}. Please select Myntra."

#     # 2. Check file count
#     if len(files) < len(MYNTRA_REQUIRED_FILES):
#         return False, f"❌ Missing files for Myntra. Expected {len(MYNTRA_REQUIRED_FILES)}, got {len(files)}."

#     # 3. Check that files exist
#     for f in files:
#         if not os.path.exists(f):
#             return False, f"❌ File not found: {f}"

#     # 4. Check that all required files are uploaded
#     for req_file in MYNTRA_REQUIRED_FILES:
#         if not any(req_file.lower() in os.path.basename(f).lower() for f in files):
#             return False, f"❌ Required file '{req_file}' missing for Myntra"

#     return True, f"✅ Payload validated successfully for Myntra (user: {user_email})"

# ---------- Myntra GSTR-1 Processor ----------
class MyntraGstr1Processor:
    def __init__(self, packed_file, rt_file=None, rto_file=None, log_file="myntra_gst.log"):
        self.packed_file = packed_file
        self.rt_file = rt_file
        self.rto_file = rto_file
        self.logger = LoggerManager.get_logger(log_file)

        # Load packed file
        try:
            self.df_packed = pd.read_csv(packed_file)
            # self.logger.info(f"Loaded packed file: {packed_file} with {len(self.df_packed)} rows")
        except Exception as e:
            self.logger.error(f"Error reading packed file {packed_file}: {e}")
            raise

        # Load RT file
        if rt_file:
            try:
                self.df_rt = pd.read_csv(rt_file)
                self.logger.info(f"Loaded RT file: {rt_file} with {len(self.df_rt)} rows")
            except Exception as e:
                self.logger.error(f"Error reading RT file {rt_file}: {e}")
                raise
        else:
            self.df_rt = None
            self.logger.info("No RT file provided.")

        # Load RTO file
        if rto_file:
            try:
                self.df_rto = pd.read_csv(rto_file)
                self.logger.info(f"Loaded RTO file: {rto_file} with {len(self.df_rto)} rows")
            except Exception as e:
                self.logger.error(f"Error reading RTO file {rto_file}: {e}")
                raise
        else:
            self.df_rto = None
            self.logger.info("No RTO file provided.")

        # State codes dictionary
        self.state_codes = {
            "ANDAMAN AND NICOBAR ISLANDS": "35",
            "ANDHRA PRADESH": "37",
            "ARUNACHAL PRADESH": "12",
            "ASSAM": "18",
            "BIHAR": "10",
            "CHANDIGARH": "04",
            "CHHATTISGARH": "22",
            "CHHATISHGARH": "22",
            "DADRA AND NAGAR HAVELI AND DAMAN AND DIU": "26",
            "DELHI": "07",
            "GOA": "30",
            "GUJARAT": "24",
            "HARYANA": "06",
            "HIMACHAL PRADESH": "02",
            "JAMMU AND KASHMIR": "01",
            "JHARKHAND": "20",
            "KARNATAKA": "29",
            "KERALA": "32",
            "MADHYA PRADESH": "23",
            "MAHARASHTRA": "27",
            "MEGHALAYA": "17",
            "NAGALAND": "13",
            "ODISHA": "21",
            "PUDUCHERRY": "34",
            "PUNJAB": "03",
            "RAJASTHAN": "08",
            "SIKKIM": "11",
            "TAMILNADU": "33",
            "TELANGANA": "36",
            "TRIPURA": "16",
            "UTTAR PRADESH": "09",
            "UTTARAKHAND": "05",
            "WEST BENGAL": "19"
        }

    def process_data(self):
        result = []
        grand_total = 0

        packed = self.df_packed.copy()
        packed["state"] = packed["location"].str.strip().str.upper()
        packed["taxable_value"] = packed["base_value"]
        packed["tax_rate"] = packed["tax_rate"]

        rt = self.df_rt.copy() if self.df_rt is not None else pd.DataFrame(columns=["delivery_state", "base_value", "tax_rate"])
        if not rt.empty:
            rt["state"] = rt["delivery_state"].str.strip().str.upper()
            rt["taxable_value"] = -rt["base_value"]

        rto = self.df_rto.copy() if self.df_rto is not None else pd.DataFrame(columns=["customer_state", "base_value", "tax_rate"])
        if not rto.empty:
            rto["state"] = rto["customer_state"].str.strip().str.upper()
            rto["taxable_value"] = -rto["base_value"]

        combined = pd.concat(
            [
                packed[["state", "tax_rate", "taxable_value"]],
                rt[["state", "tax_rate", "taxable_value"]],
                rto[["state", "tax_rate", "taxable_value"]],
            ],
            ignore_index=True
        )

        grouped = combined.groupby(["state", "tax_rate"], as_index=False)["taxable_value"].sum()

        for _, row in grouped.iterrows():
            taxable_value = round(row["taxable_value"], 2)
            if taxable_value == 0:
                continue

            state = row["state"]
            tax_rate = row["tax_rate"]
            grand_total += taxable_value
            state_code = self.state_codes.get(state.upper(), "NA")

            result.append({
                "Type": "OE",
                "Place Of Supply": f"{state_code}-{state.title()}",
                "Applicable % of Tax Rate": "",
                "Rate": tax_rate,
                "Taxable Value": taxable_value,
                "Cess Amount": 0,
                "E-Commerce GSTIN": ""
            })

            # self.logger.info(f"Processed {state} at {tax_rate}% GST: Taxable={taxable_value}")

        if grand_total != 0:
            result.append({
                "Type": "TOTAL",
                "Place Of Supply": "ALL STATES",
                "Applicable % of Tax Rate": "",
                "Rate": "",
                "Taxable Value": round(grand_total, 2),
                "Cess Amount": 0,
                "E-Commerce GSTIN": ""
            })

        return result

# ---------- MAIN SCRIPT ----------
if __name__ == "__main__":
    payload = {
        "marketplace_name": "myntra",
        "files": [
            r"C:\ganesh\ElitesecomTasks\GSTR_1\gstr_1 test files\myntra\packed.csv",
            r"C:\ganesh\ElitesecomTasks\GSTR_1\gstr_1 test files\myntra\rt.csv",
            r"C:\ganesh\ElitesecomTasks\GSTR_1\gstr_1 test files\myntra\rto.csv"
        ],
        "user_email": "rachit@example.com",
    }

    # Validate payload first
    is_valid, message = validate_payload(payload)
    print(message)

    if is_valid:
        processor = MyntraGstr1Processor(*payload["files"])
        data = processor.process_data()

        excel_file = r"C:\ganesh\ElitesecomTasks\GSTR_1\gstr_1 test files\myntra\myntra_gstr1.xlsx"
        excel_writer = ExcelWriter(excel_file, "B2CS Summary")
        excel_writer.write_data(data)
        excel_writer.save()

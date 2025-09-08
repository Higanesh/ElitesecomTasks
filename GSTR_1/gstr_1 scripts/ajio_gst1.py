import pandas as pd
from logger_manager import LoggerManager
from validate_payload import validate_payload

class AjioGSTR1Processor:
    def __init__(self, gst_file, rtv_file, output_file):
        self.gst_file = gst_file
        self.rtv_file = rtv_file
        self.output_file = output_file
        self.logger = LoggerManager().get_logger("ajio_gst.log")

    def load_files(self):
        try:
            self.gst_df = pd.read_excel(self.gst_file)
            self.rtv_df = pd.read_excel(self.rtv_file)
            self.logger.info("Loaded GST and RTV files successfully.")
        except Exception as e:
            self.logger.error(f"Error loading input files: {e}")
            raise

    def prepare_b2b(self):
        try:
            b2b_df = pd.DataFrame()
            b2b_df["Invoice Number"] = self.gst_df["Seller Invoice No"]
            b2b_df["Invoice date"] = pd.to_datetime(self.gst_df["Seller Invoice Date"].str.replace(" IST", ""), errors="coerce")
            b2b_df["Invoice Value"] = self.gst_df["Invoice Value"]
            b2b_df["Invoice Type"] = "Regular"
            b2b_df["Rate"] = (
                self.gst_df["CGST PERCENTAGE"].fillna(0)
                + self.gst_df["SGST PERCENTAGE"].fillna(0)
                + self.gst_df["IGST PERCENTAGE"].fillna(0)
            )
            b2b_df["Taxable Value"] = self.gst_df["Base Price"]
            b2b_df["Cess Amount"] = 0

            # Aggregate duplicates
            b2b_df = (
                b2b_df.groupby(["Invoice Number", "Rate", "Invoice Type"], as_index=False)
                .agg({
                    "Invoice date": "min",
                    "Invoice Value": "sum",
                    "Taxable Value": "sum",
                    "Cess Amount": "sum"
                })
            )
            b2b_df["Invoice date"] = (
    pd.to_datetime(
        b2b_df["Invoice date"].astype(str).str.replace(" IST", "", regex=False),
        errors="coerce"
    ).dt.strftime("%d-%m-%Y")
)

            self.logger.info(f"Processed {len(b2b_df)} B2B rows.")
            return b2b_df
        except Exception as e:
            self.logger.error(f"Error preparing B2B sheet: {e}")
            raise

    def prepare_cdnr(self):
        try:
            cdnr_df = pd.DataFrame()
            cdnr_df["Note Number"] = self.rtv_df["Credit Note Number"]
            cdnr_df["Note Date"] = pd.to_datetime(
                self.rtv_df["Credit Note Generation Date"].str.replace(" IST", ""), errors="coerce")
            cdnr_df["Note Type"] = "C"
            cdnr_df["Note Value"] = self.rtv_df["Credit Note Value"]
            cdnr_df["Rate"] = (
                self.rtv_df["CGST PERCENTAGE"].fillna(0)
                + self.rtv_df["SGST PERCENTAGE"].fillna(0)
                + self.rtv_df["IGST PERCENTAGE"].fillna(0)
            )
            cdnr_df["Taxable Value"] = self.rtv_df["Credit Note Pre Tax Value"]
            cdnr_df["Cess Amount"] = 0

            # Aggregate duplicates
            cdnr_df = (
                cdnr_df.groupby(["Note Number", "Rate", "Note Type"], as_index=False)
                .agg({
                    "Note Date": "min",
                    "Note Value": "sum",
                    "Taxable Value": "sum",
                    "Cess Amount": "sum"
                })
            )
            cdnr_df["Note Date"] = (
    pd.to_datetime(
        cdnr_df["Note Date"].astype(str).str.replace(" IST", "", regex=False),
        errors="coerce"
    ).dt.strftime("%d-%m-%Y")
)

            self.logger.info(f"Processed {len(cdnr_df)} CDNR rows.")
            return cdnr_df
        except Exception as e:
            self.logger.error(f"Error preparing CDNR sheet: {e}")
            raise

    def create_gstr1(self):
        try:
            b2b_df = self.prepare_b2b()
            cdnr_df = self.prepare_cdnr()

            with pd.ExcelWriter(self.output_file, engine="openpyxl") as writer:
                b2b_df.to_excel(writer, sheet_name="b2b,sez,de", index=False)
                cdnr_df.to_excel(writer, sheet_name="cdnr", index=False)

            self.logger.info(f"GSTR-1 report generated: {self.output_file}")
        except Exception as e:
            self.logger.error(f"Error creating GSTR1 report: {e}")
            raise

# ---------- MAIN SCRIPT ----------

if __name__ == "__main__":
    payload = {
            "marketplace_name": "ajio",
            "files": [
                r"C:\ganesh\ElitesecomTasks\GSTR_1\gstr_1 test files\ajio\DropShipGstReports.xlsx",
                r"C:\ganesh\ElitesecomTasks\GSTR_1\gstr_1 test files\ajio\DropShipRtvReports.xlsx",
            ],
            "user_email": "rachit@example.com",
        }

    # Validate payload first
    is_valid, message = validate_payload(payload)
    print(message)

    if is_valid:
            output_file = r"C:\ganesh\ElitesecomTasks\GSTR_1\gstr_1 test files\ajio\ajio_gstr1.xlsx"
            processor = AjioGSTR1Processor(*payload["files"],output_file)
            processor.load_files()
            processor.create_gstr1()

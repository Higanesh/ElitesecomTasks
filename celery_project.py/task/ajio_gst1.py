import os
import pandas as pd
from task.workbook import ExcelWriter

class AjioGSTR1Processor:
    def __init__(self, payload):
        """
        payload: {
            "files": ["path_to_gst_file.xlsx", "path_to_rtv_file.xlsx"]
        }
        """
        files = payload.get("files", [])
        if not files or len(files) < 2:
            raise ValueError("Payload must include two files: [gst_file, rtv_file].")

        self.gst_file = files[0]
        self.rtv_file = files[1]
        self.gst_df = None
        self.rtv_df = None

    def load_files(self):
        """Load GST and RTV Excel files."""
        self.gst_df = pd.read_excel(self.gst_file)
        self.rtv_df = pd.read_excel(self.rtv_file)

    def prepare_b2b(self):
        b2b_df = pd.DataFrame()
        b2b_df["Invoice Number"] = self.gst_df["Seller Invoice No"]
        b2b_df["Invoice date"] = pd.to_datetime(
            self.gst_df["Seller Invoice Date"].str.replace(" IST", ""), errors="coerce"
        )
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
        b2b_df["Invoice date"] = pd.to_datetime(
            b2b_df["Invoice date"].astype(str).str.replace(" IST", "", regex=False),
            errors="coerce"
        ).dt.strftime("%d-%m-%Y")

        return b2b_df

    def prepare_cdnr(self):
        cdnr_df = pd.DataFrame()
        cdnr_df["Note Number"] = self.rtv_df["Credit Note Number"]
        cdnr_df["Note Date"] = pd.to_datetime(
            self.rtv_df["Credit Note Generation Date"].str.replace(" IST", ""), errors="coerce"
        )
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
        cdnr_df["Note Date"] = pd.to_datetime(
            cdnr_df["Note Date"].astype(str).str.replace(" IST", "", regex=False),
            errors="coerce"
        ).dt.strftime("%d-%m-%Y")

        return cdnr_df


# ------------------ Handler Function ------------------
def ajio_handler(payload):
    """
    Handles Ajio GST processing and writes B2B and CDNR sheets to Excel.
    """
    processor = AjioGSTR1Processor(payload)
    processor.load_files()

    b2b_df = processor.prepare_b2b()
    cdnr_df = processor.prepare_cdnr()

    # Default output file in same folder as GST input
    gst_folder = os.path.dirname(processor.gst_file)
    output_file = "ajio_gstr1.xlsx"

    # Use your ExcelWriter
    writer = ExcelWriter(output_file, sheet_name="b2b,sez,de")
    writer.write_data(b2b_df.to_dict(orient="records"))

    # Add second sheet for CDNR
    cdnr_sheet = writer.workbook.add_worksheet("cdnr")
    writer.worksheet = cdnr_sheet
    writer.write_data(cdnr_df.to_dict(orient="records"))

    writer.save()
    return output_file


# ------------------ Manual Test ------------------
# if __name__ == "__main__":
#     payload = {
#         "files": [
#             r"C:\Users\st\Desktop\Rachit\GST_format\ajio\input_files\DropShipGstReports.xlsx",
#             r"C:\Users\st\Desktop\Rachit\GST_format\ajio\input_files\DropShipRtvReports.xlsx"
#         ]
#     }

#     result_file = ajio_handler(payload)
#     print(f"GSTR-1 Excel generated: {result_file}")
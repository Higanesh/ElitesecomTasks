import pandas as pd
from logger_manager import LoggerManager
from workbook import ExcelWriter


class MyntraGstr1Processor:
    def __init__(self, packed_file, rt_file=None, rto_file=None, log_file="myntra_gst.log"):
        self.packed_file = packed_file
        self.rt_file = rt_file
        self.rto_file = rto_file
        self.logger = LoggerManager.get_logger(log_file)

        # Load packed file
        try:
            self.df_packed = pd.read_csv(packed_file)
            self.logger.info(f"Loaded packed file: {packed_file} with {len(self.df_packed)} rows")
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

        # ✅ Packed file
        packed = self.df_packed.copy()
        packed["state"] = packed["location"].str.strip().str.upper()
        packed["taxable_value"] = packed["base_value"]
        packed["tax_rate"] = packed["tax_rate"]

        # ✅ RT file (negative taxable value)
        rt = self.df_rt.copy() if self.df_rt is not None else pd.DataFrame(columns=["delivery_state", "base_value", "tax_rate"])
        if not rt.empty:
            rt["state"] = rt["delivery_state"].str.strip().str.upper()
            rt["taxable_value"] = -rt["base_value"]

        # ✅ RTO file (negative taxable value)
        rto = self.df_rto.copy() if self.df_rto is not None else pd.DataFrame(columns=["customer_state", "base_value", "tax_rate"])
        if not rto.empty:
            rto["state"] = rto["customer_state"].str.strip().str.upper()
            rto["taxable_value"] = -rto["base_value"]

        # ✅ Merge all
        combined = pd.concat(
            [
                packed[["state", "tax_rate", "taxable_value"]],
                rt[["state", "tax_rate", "taxable_value"]],
                rto[["state", "tax_rate", "taxable_value"]],
            ],
            ignore_index=True
        )

        # ✅ Group by State + GST Rate
        grouped = combined.groupby(["state", "tax_rate"], as_index=False)["taxable_value"].sum()

        for _, row in grouped.iterrows():
            taxable_value = round(row["taxable_value"], 2)
            if taxable_value == 0:  # 🚫 skip zero values
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

            self.logger.info(f"Processed {state} at {tax_rate}% GST: Taxable={taxable_value}")

        # ✅ Grand Total
        if grand_total != 0:  # only add if not zero
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


# --------- MAIN SCRIPT ---------
if __name__ == "__main__":
    packed_file = r"D:\myProjects\ElitesecomTasks\GSTR_1\gstr_1 test files\myntra\packed.csv"
    rt_file = r"D:\myProjects\ElitesecomTasks\GSTR_1\gstr_1 test files\myntra\rt.csv"
    rto_file = r"D:\myProjects\ElitesecomTasks\GSTR_1\gstr_1 test files\myntra\rto.csv"

    processor = MyntraGstr1Processor(packed_file, rt_file, rto_file)
    data = processor.process_data()

    # Write to Excel with your common ExcelWriter
    excel_file = r"D:\myProjects\ElitesecomTasks\GSTR_1\gstr_1 test files\myntra\myntra_gstr1.xlsx"
    excel_writer = ExcelWriter(excel_file, "B2CS Summary")
    excel_writer.write_data(data)
    excel_writer.save()









import pandas as pd
from logger_manager import LoggerManager

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


# if __name__ == "__main__":
#     gst_file = r"D:\myProjects\ElitesecomTasks\I-O Files\gstr_1 test files\ajio\DropShipGstReports.xlsx"
#     rtv_file = r"D:\myProjects\ElitesecomTasks\I-O Files\gstr_1 test files\ajio\DropShipRtvReports.xlsx"
#     output_file = r"D:\myProjects\ElitesecomTasks\I-O Files\gstr_1 test files\ajio\ajio_gstr1.xlsx"

#     processor = AjioGSTR1Processor(gst_file, rtv_file, output_file)
#     processor.load_files()
#     processor.create_gstr1()

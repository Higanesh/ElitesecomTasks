import os
import pandas as pd
from task.workbook import ExcelWriter


class MyntraGstr1Processor:
    def __init__(self, payload):
        """
        payload: {
            "files": ["packed_file.csv", "rt_file.csv", "rto_file.csv"]  # RT and RTO optional
        }
        """
        files = payload.get("files", [])
        if not files or len(files) < 1:
            raise ValueError("Payload must include at least the packed_file CSV.")

        self.packed_file = files[0]
        self.rt_file = files[1] if len(files) > 1 else None
        self.rto_file = files[2] if len(files) > 2 else None

        # Load packed file
        try:
            self.df_packed = pd.read_csv(self.packed_file)
        except Exception as e:
            raise

        # Load RT file
        if self.rt_file:
            try:
                self.df_rt = pd.read_csv(self.rt_file)
            except Exception as e:
                raise
        else:
            self.df_rt = None

        # Load RTO file
        if self.rto_file:
            try:
                self.df_rto = pd.read_csv(self.rto_file)
            except Exception as e:
                raise
        else:
            self.df_rto = None

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

        # Packed file
        packed = self.df_packed.copy()
        packed["state"] = packed["location"].str.strip().str.upper()
        packed["taxable_value"] = packed["base_value"]
        packed["tax_rate"] = packed["tax_rate"]

        # RT file (negative taxable value)
        rt = self.df_rt.copy() if self.df_rt is not None else pd.DataFrame(columns=["delivery_state", "base_value", "tax_rate"])
        if not rt.empty:
            rt["state"] = rt["delivery_state"].str.strip().str.upper()
            rt["taxable_value"] = -rt["base_value"]

        # RTO file (negative taxable value)
        rto = self.df_rto.copy() if self.df_rto is not None else pd.DataFrame(columns=["customer_state", "base_value", "tax_rate"])
        if not rto.empty:
            rto["state"] = rto["customer_state"].str.strip().str.upper()
            rto["taxable_value"] = -rto["base_value"]

        # Merge all
        combined = pd.concat(
            [
                packed[["state", "tax_rate", "taxable_value"]],
                rt[["state", "tax_rate", "taxable_value"]],
                rto[["state", "tax_rate", "taxable_value"]],
            ],
            ignore_index=True
        )

        # Group by State + GST Rate
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


        # Grand Total
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


# ---------------- Handler with Save ----------------
def myntra_handler(payload, output_file=None):
    processor = MyntraGstr1Processor(payload)
    data = processor.process_data()

    # Default output file
    if not output_file:
        folder = os.path.dirname(processor.packed_file)
        output_file = "myntra_gstr1.xlsx"

    excel_writer = ExcelWriter(output_file, "B2CS Summary")
    excel_writer.write_data(data)
    excel_writer.save()
    return output_file


# ---------------- Manual Test ----------------
if __name__ == "__main__":
    payload = {
        "files": [
            r"C:\Users\st\Desktop\Rachit\GST_format\myntra\Input_files\packed.csv",
            r"C:\Users\st\Desktop\Rachit\GST_format\myntra\Input_files\rt.csv",
            r"C:\Users\st\Desktop\Rachit\GST_format\myntra\Input_files\rto.csv"
        ]
    }

    excel_file = myntra_handler(payload)
    print(f"Myntra GSTR-1 Excel saved at: {excel_file}")
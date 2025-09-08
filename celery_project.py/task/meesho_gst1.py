import pandas as pd
from task.workbook import ExcelWriter

class TcsSalesProcessorMeesho:
    def __init__(self, payload, log_file="meesho_gst1.log"):
        """
        payload: {
            "files": ["sales_file.xlsx", "returns_file.xlsx"]  # returns_file optional
        }
        """

        files = payload.get("files", [])
        if not files or len(files) == 0:
            raise ValueError("Payload must contain at least one file (sales file).")

        self.sales_file = files[0]
        self.returns_file = files[1] if len(files) > 1 else None

        # Load sales file
        try:
            self.df_sales = pd.read_excel(self.sales_file)
        except Exception as e:
            raise

        # Load returns file if provided
        if self.returns_file:
            try:
                self.df_returns = pd.read_excel(self.returns_file)
            except Exception as e:
                raise
        else:
            self.df_returns = None

        self.state_codes = {
            "ANDAMAN AND NICOBAR ISLANDS": "35",
            "ANDHRA PRADESH": "37",
            "ARUNACHAL PRADESH": "12",
            "ASSAM": "18",
            "BIHAR": "10",
            "CHANDIGARH": "04",
            "CHHATTISGARH": "22",
            "THE DADRA AND NAGAR HAVELI AND DAMAN AND DIU": "26",
            "DELHI": "07",
            "GOA": "30",
            "GUJARAT": "24",
            "HARYANA": "06",
            "JAMMU AND KASHMIR": "01",
            "JHARKHAND": "20",
            "KARNATAKA": "29",
            "KERALA": "32",
            "MADHYA PRADESH": "23",
            "MAHARASHTRA": "27",
            "MEGHALAYA": "17",
            "NAGALAND": "13",
            "ODISHA": "21",
            "PONDICHERRY": "34",
            "PUNJAB": "03",
            "RAJASTHAN": "08",
            "TAMIL NADU": "33",
            "TELANGANA": "36",
            "TRIPURA": "16",
            "UTTAR PRADESH": "09",
            "UTTARAKHAND": "05",
            "WEST BENGAL": "19"
        }


    def process_data(self):
        result = []
        grand_total = 0

        for (state, gst_rate), group in self.df_sales.groupby(["end_customer_state_new", "gst_rate"]):
            total_sales = round(group["total_taxable_sale_value"].sum(), 2)

            total_returns = 0
            if self.df_returns is not None:
                state_returns = self.df_returns[
                    (self.df_returns["end_customer_state_new"] == state) & 
                    (self.df_returns["gst_rate"] == gst_rate)
                ]
                total_returns = round(state_returns["total_taxable_sale_value"].sum(), 2)

            net_taxable = round(total_sales - total_returns, 2)
            grand_total += net_taxable

            state_code = self.state_codes.get(state.upper(), "NA")

            result.append({
                "Type": "OE",
                "Place Of Supply": f"{state_code}-{state.title()}",
                "Applicable % of Tax Rate": "",
                "Rate": gst_rate,
                "Taxable Value": net_taxable,
                "Cess Amount": 0,
                "E-Commerce GSTIN": ""
            })


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




def meesho_handler(payload, output_file="output.xlsx", sheet_name="GST Report"):
    processor = TcsSalesProcessorMeesho(payload)
    processed_data = processor.process_data()

    excel_writer = ExcelWriter(output_file, sheet_name)
    excel_writer.write_data(processed_data)
    excel_writer.save()

    return f"Processed successfully! Excel saved at {output_file}"    

if __name__ == "__main__":
    payload = {
        "files": [
            r"C:\Users\st\Desktop\Rachit\GST_format\meesho\Input_file\tcs_sales.xlsx",
            r"C:\Users\st\Desktop\Rachit\GST_format\meesho\Input_file\tcs_sales_return.xlsx"
        ]
    }
    print(meesho_handler(payload))
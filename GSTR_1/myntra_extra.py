# # import pandas as pd
# # import logging
# # import xlsxwriter


# # class MyntraGstr1Processor:
# #     def __init__(self, packed_file, rt_file=None, rto_file=None, log_file="myntra_gstr1.log"):
# #         self.packed_file = packed_file
# #         self.rt_file = rt_file
# #         self.rto_file = rto_file

# #         # Setup logger
# #         logging.basicConfig(
# #             filename=log_file,
# #             level=logging.INFO,
# #             format="%(asctime)s - %(levelname)s - %(message)s"
# #         )
# #         self.logger = logging.getLogger(__name__)

# #         # Load packed file
# #         try:
# #             self.df_packed = pd.read_csv(packed_file)
# #             self.logger.info(f"Loaded packed file: {packed_file} with {len(self.df_packed)} rows")
# #         except Exception as e:
# #             self.logger.error(f"Error reading packed file {packed_file}: {e}")
# #             raise

# #         # Load RT file
# #         if rt_file:
# #             try:
# #                 self.df_rt = pd.read_csv(rt_file)
# #                 self.logger.info(f"Loaded RT file: {rt_file} with {len(self.df_rt)} rows")
# #             except Exception as e:
# #                 self.logger.error(f"Error reading RT file {rt_file}: {e}")
# #                 raise
# #         else:
# #             self.df_rt = None
# #             self.logger.info("No RT file provided.")

# #         # Load RTO file
# #         if rto_file:
# #             try:
# #                 self.df_rto = pd.read_csv(rto_file)
# #                 self.logger.info(f"Loaded RTO file: {rto_file} with {len(self.df_rto)} rows")
# #             except Exception as e:
# #                 self.logger.error(f"Error reading RTO file {rto_file}: {e}")
# #                 raise
# #         else:
# #             self.df_rto = None
# #             self.logger.info("No RTO file provided.")

# #         # State codes dictionary
# #         self.state_codes = {
# #             "ANDAMAN AND NICOBAR ISLANDS": "35",
# #             "ANDHRA PRADESH": "37",
# #             "ARUNACHAL PRADESH": "12",
# #             "ASSAM": "18",
# #             "BIHAR": "10",
# #             "CHANDIGARH": "04",
# #             "CHHATTISGARH": "22",
# #             "DADRA AND NAGAR HAVELI AND DAMAN AND DIU": "26",
# #             "DELHI": "07",
# #             "GOA": "30",
# #             "GUJARAT": "24",
# #             "HARYANA": "06",
# #             "JAMMU AND KASHMIR": "01",
# #             "JHARKHAND": "20",
# #             "KARNATAKA": "29",
# #             "KERALA": "32",
# #             "MADHYA PRADESH": "23",
# #             "MAHARASHTRA": "27",
# #             "MEGHALAYA": "17",
# #             "NAGALAND": "13",
# #             "ODISHA": "21",
# #             "PUDUCHERRY": "34",
# #             "PUNJAB": "03",
# #             "RAJASTHAN": "08",
# #             "TAMIL NADU": "33",
# #             "TELANGANA": "36",
# #             "TRIPURA": "16",
# #             "UTTAR PRADESH": "09",
# #             "UTTARAKHAND": "05",
# #             "WEST BENGAL": "19"
# #         }

# #     def process_data(self):
# #         result = []
# #         grand_total = 0

# #         # ✅ Packed file
# #         packed = self.df_packed.copy()
# #         packed["state"] = packed["location"].str.strip().str.upper()
# #         packed["taxable_value"] = packed["base_value"]
# #         packed["tax_rate"] = packed["tax_rate"]  # already exists

# #         # ✅ RT file (negative taxable value)
# #         rt = self.df_rt.copy() if self.df_rt is not None else pd.DataFrame(columns=["delivery_state", "base_value", "tax_rate"])
# #         if not rt.empty:
# #             rt["state"] = rt["delivery_state"].str.strip().str.upper()
# #             rt["taxable_value"] = -rt["base_value"]

# #         # ✅ RTO file (negative taxable value)
# #         rto = self.df_rto.copy() if self.df_rto is not None else pd.DataFrame(columns=["customer_state", "base_value", "tax_rate"])
# #         if not rto.empty:
# #             rto["state"] = rto["customer_state"].str.strip().str.upper()
# #             rto["taxable_value"] = -rto["base_value"]

# #         # ✅ Merge all
# #         combined = pd.concat(
# #             [
# #                 packed[["state", "tax_rate", "taxable_value"]],
# #                 rt[["state", "tax_rate", "taxable_value"]],
# #                 rto[["state", "tax_rate", "taxable_value"]],
# #             ],
# #             ignore_index=True
# #         )

# #         # ✅ Group by State + GST Rate
# #         grouped = combined.groupby(["state", "tax_rate"], as_index=False)["taxable_value"].sum()

# #         for _, row in grouped.iterrows():
# #             state = row["state"]
# #             tax_rate = row["tax_rate"]
# #             taxable_value = round(row["taxable_value"], 2)
# #             grand_total += taxable_value
# #             state_code = self.state_codes.get(state.upper(), "NA")

# #             result.append({
# #                 "Type": "OE",
# #                 "Place Of Supply": f"{state_code}-{state.title()}",
# #                 "Applicable % of Tax Rate": "",
# #                 "Rate": tax_rate,
# #                 "Taxable Value": taxable_value,
# #                 "Cess Amount": 0,
# #                 "E-Commerce GSTIN": ""
# #             })

# #             self.logger.info(f"Processed {state} at {tax_rate}% GST: Taxable={taxable_value}")

# #         # ✅ Grand Total
# #         result.append({
# #             "Type": "TOTAL",
# #             "Place Of Supply": "ALL STATES",
# #             "Applicable % of Tax Rate": "",
# #             "Rate": "",
# #             "Taxable Value": round(grand_total, 2),
# #             "Cess Amount": 0,
# #             "E-Commerce GSTIN": ""
# #         })

# #         return result


# # # --------- MAIN SCRIPT ---------
# # if __name__ == "__main__":
# #     packed_file = r"C:\ganesh\ElitesecomTasks\I-O Files\gstr_1 test files\myntra\packed.csv"
# #     rt_file = r"C:\ganesh\ElitesecomTasks\I-O Files\gstr_1 test files\myntra\rt.csv"
# #     rto_file = r"C:\ganesh\ElitesecomTasks\I-O Files\gstr_1 test files\myntra\rto.csv"

# #     processor = MyntraGstr1Processor(packed_file, rt_file, rto_file)
# #     processed_data = processor.process_data()

# #     # Save Excel
# #     excel_file = r"C:\ganesh\ElitesecomTasks\I-O Files\gstr_1 test files\myntra\myntra_gstr1.xlsx"
# #     workbook = xlsxwriter.Workbook(excel_file)
# #     worksheet = workbook.add_worksheet("GST Report")

# #     # Header format (green background, bold, white text)
# #     header_format = workbook.add_format({
# #         "bold": True,
# #         "bg_color": "#92D050",
# #         "font_color": "white",
# #         "border": 1,
# #         "align": "center",
# #         "valign": "vcenter"
# #     })

# #     # Normal cell format
# #     cell_format = workbook.add_format({
# #         "border": 1,
# #         "align": "center",
# #         "valign": "vcenter"
# #     })

# #     # Write headers
# #     headers = list(processed_data[0].keys())
# #     for col_num, header in enumerate(headers):
# #         worksheet.write(0, col_num, header, header_format)

# #     # Write data rows
# #     for row_num, row_data in enumerate(processed_data, start=1):
# #         for col_num, (key, value) in enumerate(row_data.items()):
# #             worksheet.write(row_num, col_num, value, cell_format)

# #     # Auto column width
# #     for col_num, header in enumerate(headers):
# #         worksheet.set_column(col_num, col_num, 25)

# #     workbook.close()
# #     print(f"✅ Excel report saved to {excel_file} with GST rate breakup")









# # import pandas as pd
# # from logger_manager import LoggerManager
# # from workbook import ExcelWriter


# # class MyntraGstr1Processor:
# #     def __init__(self, packed_file, rt_file=None, rto_file=None, log_file="myntra_gstr1.log"):
# #         self.packed_file = packed_file
# #         self.rt_file = rt_file
# #         self.rto_file = rto_file
# #         self.logger = LoggerManager.get_logger(log_file)

# #         # State codes dictionary
# #         self.state_codes = {
# #             "ANDAMAN AND NICOBAR ISLANDS": "35-Andaman and Nicobar Islands",
# #             "ANDHRA PRADESH": "37-Andhra Pradesh",
# #             "ARUNACHAL PRADESH": "12-Arunachal Pradesh",
# #             "ASSAM": "18-Assam",
# #             "BIHAR": "10-Bihar",
# #             "CHANDIGARH": "04-Chandigarh",
# #             "CHHATTISGARH": "22-Chhattisgarh",
# #             "DADRA AND NAGAR HAVELI AND DAMAN AND DIU": "26-Dadra & Nagar Haveli & Daman & Diu",
# #             "DELHI": "07-Delhi",
# #             "GOA": "30-Goa",
# #             "GUJARAT": "24-Gujarat",
# #             "HARYANA": "06-Haryana",
# #             "JAMMU AND KASHMIR": "01-Jammu and Kashmir",
# #             "JHARKHAND": "20-Jharkhand",
# #             "KARNATAKA": "29-Karnataka",
# #             "KERALA": "32-Kerala",
# #             "MADHYA PRADESH": "23-Madhya Pradesh",
# #             "MAHARASHTRA": "27-Maharashtra",
# #             "MEGHALAYA": "17-Meghalaya",
# #             "NAGALAND": "13-Nagaland",
# #             "ODISHA": "21-Odisha",
# #             "PUDUCHERRY": "34-Puducherry",
# #             "PUNJAB": "03-Punjab",
# #             "RAJASTHAN": "08-Rajasthan",
# #             "TAMIL NADU": "33-Tamil Nadu",
# #             "TELANGANA": "36-Telangana",
# #             "TRIPURA": "16-Tripura",
# #             "UTTAR PRADESH": "09-Uttar Pradesh",
# #             "UTTARAKHAND": "05-Uttarakhand",
# #             "WEST BENGAL": "19-West Bengal"
# #         }

# #     def process(self):
# #         result = []
# #         grand_total = 0

# #         # ✅ Load packed file
# #         df_packed = pd.read_csv(self.packed_file)
# #         df_packed["state"] = df_packed["location"].str.strip().str.upper()
# #         df_packed["taxable_value"] = df_packed["base_value"]
# #         df_packed["tax_rate"] = df_packed["tax_rate"]

# #         # ✅ Load RT file
# #         df_rt = pd.DataFrame(columns=["delivery_state", "base_value", "tax_rate"])
# #         if self.rt_file:
# #             df_rt = pd.read_csv(self.rt_file)
# #             df_rt["state"] = df_rt["delivery_state"].str.strip().str.upper()
# #             df_rt["taxable_value"] = -df_rt["base_value"]

# #         # ✅ Load RTO file
# #         df_rto = pd.DataFrame(columns=["customer_state", "base_value", "tax_rate"])
# #         if self.rto_file:
# #             df_rto = pd.read_csv(self.rto_file)
# #             df_rto["state"] = df_rto["customer_state"].str.strip().str.upper()
# #             df_rto["taxable_value"] = -df_rto["base_value"]

# #         # ✅ Combine all
# #         combined = pd.concat(
# #             [
# #                 df_packed[["state", "tax_rate", "taxable_value"]],
# #                 df_rt[["state", "tax_rate", "taxable_value"]],
# #                 df_rto[["state", "tax_rate", "taxable_value"]],
# #             ],
# #             ignore_index=True
# #         )

# #         # ✅ Group by State + GST Rate
# #         grouped = combined.groupby(["state", "tax_rate"], as_index=False)["taxable_value"].sum()

# #         for _, row in grouped.iterrows():
# #             state = row["state"]
# #             tax_rate = row["tax_rate"]
# #             taxable_value = round(row["taxable_value"], 2)
# #             grand_total += taxable_value
# #             place_of_supply = self.state_codes.get(state.upper(), state.title())

# #             result.append({
# #                 "Type": "OE",
# #                 "Place Of Supply": place_of_supply,
# #                 "Applicable % of Tax Rate": "",
# #                 "Rate": tax_rate,
# #                 "Taxable Value": taxable_value,
# #                 "Cess Amount": 0,
# #                 "E-Commerce GSTIN": ""
# #             })

# #             self.logger.info(f"Processed {state} at {tax_rate}% GST: Taxable={taxable_value}")

# #         # ✅ Grand Total Row
# #         result.append({
# #             "Type": "TOTAL",
# #             "Place Of Supply": "ALL STATES",
# #             "Applicable % of Tax Rate": "",
# #             "Rate": "",
# #             "Taxable Value": round(grand_total, 2),
# #             "Cess Amount": 0,
# #             "E-Commerce GSTIN": ""
# #         })

# #         return result


# # # ------------------ Manual Test ------------------
# # if __name__ == "__main__":
# #     packed_file = r"C:\ganesh\ElitesecomTasks\I-O Files\gstr_1 test files\myntra\packed.csv"
# #     rt_file = r"C:\ganesh\ElitesecomTasks\I-O Files\gstr_1 test files\myntra\rt.csv"
# #     rto_file = r"C:\ganesh\ElitesecomTasks\I-O Files\gstr_1 test files\myntra\rto.csv"
# #     output_file = r"C:\ganesh\ElitesecomTasks\I-O Files\gstr_1 test files\myntra\myntra_gstr1.xlsx"

# #     processor = MyntraGstr1Processor(packed_file, rt_file, rto_file)

# #     try:
# #         data = processor.process()

# #         # Use your existing ExcelWriter class
# #         excel_writer = ExcelWriter(output_file, "B2CS Summary")
# #         excel_writer.write_data(data)
# #         excel_writer.save()

# #     except Exception as e:
# #         processor.logger.error(f"Error during processing: {e}")
# #         raise









# import pandas as pd
# from logger_manager import LoggerManager
# from workbook import ExcelWriter


# class MyntraGstr1Processor:
#     def __init__(self, packed_file, rt_file=None, rto_file=None, log_file="myntra_gstr1.log"):
#         self.packed_file = packed_file
#         self.rt_file = rt_file
#         self.rto_file = rto_file
#         self.logger = LoggerManager.get_logger(log_file)

#         # Load packed file
#         try:
#             self.df_packed = pd.read_csv(packed_file)
#             self.logger.info(f"Loaded packed file: {packed_file} with {len(self.df_packed)} rows")
#         except Exception as e:
#             self.logger.error(f"Error reading packed file {packed_file}: {e}")
#             raise

#         # Load RT file
#         if rt_file:
#             try:
#                 self.df_rt = pd.read_csv(rt_file)
#                 self.logger.info(f"Loaded RT file: {rt_file} with {len(self.df_rt)} rows")
#             except Exception as e:
#                 self.logger.error(f"Error reading RT file {rt_file}: {e}")
#                 raise
#         else:
#             self.df_rt = None
#             self.logger.info("No RT file provided.")

#         # Load RTO file
#         if rto_file:
#             try:
#                 self.df_rto = pd.read_csv(rto_file)
#                 self.logger.info(f"Loaded RTO file: {rto_file} with {len(self.df_rto)} rows")
#             except Exception as e:
#                 self.logger.error(f"Error reading RTO file {rto_file}: {e}")
#                 raise
#         else:
#             self.df_rto = None
#             self.logger.info("No RTO file provided.")

#         # State codes dictionary
#         self.state_codes = {
#             "ANDAMAN AND NICOBAR ISLANDS": "35",
#             "ANDHRA PRADESH": "37",
#             "ARUNACHAL PRADESH": "12",
#             "ASSAM": "18",
#             "BIHAR": "10",
#             "CHANDIGARH": "04",
#             "CHHATTISGARH": "22",
#             "CHHATISHGARH": "22",
#             "DADRA AND NAGAR HAVELI AND DAMAN AND DIU": "26",
#             "DELHI": "07",
#             "GOA": "30",
#             "GUJARAT": "24",
#             "HARYANA": "06",
#             "HIMACHAL PRADESH": "02",
#             "JAMMU AND KASHMIR": "01",
#             "JHARKHAND": "20",
#             "KARNATAKA": "29",
#             "KERALA": "32",
#             "MADHYA PRADESH": "23",
#             "MAHARASHTRA": "27",
#             "MEGHALAYA": "17",
#             "NAGALAND": "13",
#             "ODISHA": "21",
#             "PUDUCHERRY": "34",
#             "PUNJAB": "03",
#             "RAJASTHAN": "08",
#             "SIKKIM": "11",
#             "TAMILNADU": "33",
#             "TELANGANA": "36",
#             "TRIPURA": "16",
#             "UTTAR PRADESH": "09",
#             "UTTARAKHAND": "05",
#             "WEST BENGAL": "19"
#         }

#     def process_data(self):
#         result = []
#         grand_total = 0

#         # ✅ Packed file
#         packed = self.df_packed.copy()
#         packed["state"] = packed["location"].str.strip().str.upper()
#         packed["taxable_value"] = packed["base_value"]
#         packed["tax_rate"] = packed["tax_rate"]

#         # ✅ RT file (negative taxable value)
#         rt = self.df_rt.copy() if self.df_rt is not None else pd.DataFrame(columns=["delivery_state", "base_value", "tax_rate"])
#         if not rt.empty:
#             rt["state"] = rt["delivery_state"].str.strip().str.upper()
#             rt["taxable_value"] = -rt["base_value"]

#         # ✅ RTO file (negative taxable value)
#         rto = self.df_rto.copy() if self.df_rto is not None else pd.DataFrame(columns=["customer_state", "base_value", "tax_rate"])
#         if not rto.empty:
#             rto["state"] = rto["customer_state"].str.strip().str.upper()
#             rto["taxable_value"] = -rto["base_value"]

#         # ✅ Merge all
#         combined = pd.concat(
#             [
#                 packed[["state", "tax_rate", "taxable_value"]],
#                 rt[["state", "tax_rate", "taxable_value"]],
#                 rto[["state", "tax_rate", "taxable_value"]],
#             ],
#             ignore_index=True
#         )

#         # ✅ Group by State + GST Rate
#         grouped = combined.groupby(["state", "tax_rate"], as_index=False)["taxable_value"].sum()

#         for _, row in grouped.iterrows():
#             taxable_value = round(row["taxable_value"], 2)
#             if taxable_value == 0:  # 🚫 skip zero values
#                 continue

#             state = row["state"]
#             tax_rate = row["tax_rate"]
#             grand_total += taxable_value
#             state_code = self.state_codes.get(state.upper(), "NA")

#             result.append({
#                 "Type": "OE",
#                 "Place Of Supply": f"{state_code}-{state.title()}",
#                 "Applicable % of Tax Rate": "",
#                 "Rate": tax_rate,
#                 "Taxable Value": taxable_value,
#                 "Cess Amount": 0,
#                 "E-Commerce GSTIN": ""
#             })

#             self.logger.info(f"Processed {state} at {tax_rate}% GST: Taxable={taxable_value}")

#         # ✅ Grand Total
#         if grand_total != 0:  # only add if not zero
#             result.append({
#                 "Type": "TOTAL",
#                 "Place Of Supply": "ALL STATES",
#                 "Applicable % of Tax Rate": "",
#                 "Rate": "",
#                 "Taxable Value": round(grand_total, 2),
#                 "Cess Amount": 0,
#                 "E-Commerce GSTIN": ""
#             })

#         return result


# # --------- MAIN SCRIPT ---------
# if __name__ == "__main__":
#     packed_file = r"C:\ganesh\ElitesecomTasks\I-O Files\gstr_1 test files\myntra\packed.csv"
#     rt_file = r"C:\ganesh\ElitesecomTasks\I-O Files\gstr_1 test files\myntra\rt.csv"
#     rto_file = r"C:\ganesh\ElitesecomTasks\I-O Files\gstr_1 test files\myntra\rto.csv"

#     processor = MyntraGstr1Processor(packed_file, rt_file, rto_file)
#     data = processor.process_data()

#     # Write to Excel with your common ExcelWriter
#     excel_file = r"C:\ganesh\ElitesecomTasks\I-O Files\gstr_1 test files\myntra\myntra_gstr1.xlsx"
#     excel_writer = ExcelWriter(excel_file, "B2CS Summary")
#     excel_writer.write_data(data)
#     excel_writer.save()

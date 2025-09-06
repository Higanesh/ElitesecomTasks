import xlsxwriter

# ------------------ Excel Formats ------------------
class ExcelFormats:
    """Defines reusable Excel formats"""
    @staticmethod
    def header_format(workbook):
        return workbook.add_format({
            "bold": True,
            "bg_color": "#92D050",
            "font_color": "white",
            "border": 1,
            "align": "center",
            "valign": "vcenter"
        })

    @staticmethod
    def cell_format(workbook):
        return workbook.add_format({
            "border": 1,
            "align": "center",
            "valign": "vcenter"
        })


# ------------------ Excel Writer ------------------
class ExcelWriter:
    """Writes data to Excel using formats"""
    def __init__(self, file_name, sheet_name="Sheet1"):
        self.file_name = file_name
        self.sheet_name = sheet_name
        self.workbook = xlsxwriter.Workbook(file_name)
        self.worksheet = self.workbook.add_worksheet(sheet_name)
        self.header_fmt = ExcelFormats.header_format(self.workbook)
        self.cell_fmt = ExcelFormats.cell_format(self.workbook)

    def write_data(self, data):
        """data: list of dicts"""
        if not data:
            return

        # Write headers
        headers = list(data[0].keys())
        for col_num, header in enumerate(headers):
            self.worksheet.write(0, col_num, header, self.header_fmt)

        # Write rows
        for row_num, row_data in enumerate(data, start=1):
            for col_num, (key, value) in enumerate(row_data.items()):
                self.worksheet.write(row_num, col_num, value, self.cell_fmt)

        # Auto-adjust column width
        for col_num, header in enumerate(headers):
            self.worksheet.set_column(col_num, col_num, 20)

    def save(self):
        self.workbook.close()
        print(f"✅ Excel file saved: {self.file_name}")











        

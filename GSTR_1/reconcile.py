import pandas as pd
import openpyxl

# ==============================
# File paths (update as needed)
# ==============================
gstr1_file = r"C:\ganesh\ElitesecomTasks\I-O Files\gstr_1 test files\myntra\GSTR1_24AMVPN8776H1Z5_monthly_072025.xlsx"
packed_file = r"C:\ganesh\ElitesecomTasks\I-O Files\gstr_1 test files\myntra\packed.csv"
rt_file = r"C:\ganesh\ElitesecomTasks\I-O Files\gstr_1 test files\myntra\rt.csv"
rto_file = r"C:\ganesh\ElitesecomTasks\I-O Files\gstr_1 test files\myntra\rto.csv"
output_file = r"C:\ganesh\ElitesecomTasks\I-O Files\gstr_1 test files\myntra\GSTR1_Reconciliation.xlsx"

# ==============================
# Step 1: Load GSTR-1 B2CS data
# ==============================
# Assuming "B2CS" or "Summary For B2CS(7)" sheet
gstr1_df = pd.read_excel(gstr1_file, sheet_name="b2cs", skiprows=3)
gstr1_df = gstr1_df[["Place Of Supply", "Taxable Value"]]
gstr1_df.rename(columns={"Place Of Supply": "state", "Taxable Value": "gstr1_value"}, inplace=True)

# ==============================
# Step 2: Load sales files
# ==============================
# Packed
packed = pd.read_csv(packed_file)
packed = packed.rename(columns={"location": "state"})
packed["taxable_value"] = packed["taxable_value"].astype(float)
packed["net_value"] = packed["taxable_value"]

# RT (returns)
rt = pd.read_csv(rt_file)
rt = rt.rename(columns={"delivery_state": "state"})
rt["taxable_value"] = rt["taxable_value"].astype(float)
rt["net_value"] = -rt["taxable_value"]

# RTO
rto = pd.read_csv(rto_file)
rto = rto.rename(columns={"customer_state": "state"})
rto["taxable_value"] = rto["taxable_value"].astype(float)
rto["net_value"] = -rto["taxable_value"]

# ==============================
# Step 3: Combine all sales data
# ==============================
sales_all = pd.concat([packed[["state", "net_value"]],
                       rt[["state", "net_value"]],
                       rto[["state", "net_value"]]])

# ==============================
# Step 4: Aggregate by state
# ==============================
sales_summary = sales_all.groupby("state", as_index=False).sum()
sales_summary.rename(columns={"net_value": "sales_value"}, inplace=True)

# ==============================
# Step 5: Merge with GSTR-1
# ==============================
comparison = pd.merge(sales_summary, gstr1_df,
                      on="state", how="outer")

comparison["difference"] = comparison["sales_value"].fillna(0) - comparison["gstr1_value"].fillna(0)

# ==============================
# Step 6: Categorize results
# ==============================
matched = comparison[comparison["difference"] == 0]
mismatched = comparison[comparison["difference"] != 0]
missing_sales = comparison[comparison["sales_value"].isna()]
missing_gstr1 = comparison[comparison["gstr1_value"].isna()]

# ==============================
# Step 7: Save to Excel
# ==============================
with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
    matched.to_excel(writer, sheet_name="Matched", index=False)
    mismatched.to_excel(writer, sheet_name="Mismatched", index=False)
    missing_sales.to_excel(writer, sheet_name="Missing in Sales", index=False)
    missing_gstr1.to_excel(writer, sheet_name="Missing in GSTR1", index=False)

print(f"✅ Reconciliation completed. Output saved to: {output_file}")

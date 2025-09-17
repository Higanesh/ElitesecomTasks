from flask import Flask, request, jsonify
import pandas as pd
import numpy as np

app = Flask(__name__)
SELLER_STATE = "GUJARAT"  # Change this as per your GST registration state

def calculate_summary(sales_df, returns_df):
    summary = {}

    # Net values (Sales - Returns)
    taxable = sales_df["total_taxable_sale_value"].sum() - returns_df["total_taxable_sale_value"].sum()
    tax = sales_df["tax_amount"].sum() - returns_df["tax_amount"].sum()
    invoice = sales_df["total_invoice_value"].sum() - returns_df["total_invoice_value"].sum()

    # IGST: interstate (customer state != seller state)
    sales_inter = sales_df[sales_df["end_customer_state_new"] != SELLER_STATE]
    returns_inter = returns_df[returns_df["end_customer_state_new"] != SELLER_STATE]
    igst = sales_inter["tax_amount"].sum() - returns_inter["tax_amount"].sum()

    # CGST + SGST: intrastate (customer state = seller state)
    sales_intra = sales_df[sales_df["end_customer_state_new"] == SELLER_STATE]
    returns_intra = returns_df[returns_df["end_customer_state_new"] == SELLER_STATE]
    cgst = (sales_intra["tax_amount"].sum() - returns_intra["tax_amount"].sum()) / 2
    sgst = cgst

    # Total Summary
    summary["Total"] = {
        "sales_amount": round(taxable, 2),
        "igst": round(igst, 2),
        "cgst": round(cgst, 2),
        "sgst": round(sgst, 2),
        "invoice_amount": round(invoice, 2)
    }

    # HSN-wise Summary
    hsn_sales = sales_df.groupby("hsn_code")["total_taxable_sale_value"].sum()
    hsn_returns = returns_df.groupby("hsn_code")["total_taxable_sale_value"].sum()
    hsn_summary = (hsn_sales - hsn_returns).fillna(0).to_dict()
    summary["HSN_Wise"] = hsn_summary

    return summary

# Recursive function to convert all numpy/pandas types
def convert_numpy(obj):
    if isinstance(obj, dict):
        return {k: convert_numpy(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy(x) for x in obj]
    elif isinstance(obj, (np.integer,)):
        return int(obj)
    elif isinstance(obj, (np.floating,)):
        return float(obj)
    elif isinstance(obj, (np.ndarray, pd.Series)):
        return obj.tolist()
    else:
        return obj

@app.route("/gstr-summary", methods=["POST"])
def gstr_summary():
    sales_file = request.files["sales"]
    returns_file = request.files["returns"]

    sales_df = pd.read_excel(sales_file)
    returns_df = pd.read_excel(returns_file)

    summary = calculate_summary(sales_df, returns_df)

    # Convert all numpy/pandas types recursively
    summary_clean = convert_numpy(summary)

    return jsonify(summary_clean)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

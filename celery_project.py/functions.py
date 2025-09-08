from task.limeroad_gst1 import limeroad_handler
from task.meesho_gst1 import meesho_handler
from task.flipcart_gst1 import flipcart_handler
from task.snapdeal_gst1 import snapdeal_handler
from task.ajio_gst1 import ajio_handler
from task.myntra_gst1 import myntra_handler

meesho_payload = {"marketplace_name" : "meesho" ,
           "files": [
            r"C:\Users\st\Desktop\Rachit\GST_format\meesho\Input_file\tcs_sales.xlsx",
            r"C:\Users\st\Desktop\Rachit\GST_format\meesho\Input_file\tcs_sales_return.xlsx"
        ],
           "user_email" : "rachit" ,
           }

limeroad_payload = {"marketplace_name" : "limeroad" ,
           "files": [
            r"C:\Users\st\Desktop\Rachit\GST_format\Limeroad\input_files\limeroad_report.xlsx"
        ],
           "user_email" : "rachit" ,
           }

flipcart_payload = {"marketplace_name" : "flipcart" ,
        "files": [
            r"C:\Users\st\Desktop\Rachit\GST_format\Flipcart\input_files\sales_report.xlsx"
        ],
            "user_email" : "rachit" ,
            }

snapdeal_payload = {"marketplace_name" : "snapdeal" ,
                    "files": [r"C:\Users\st\Desktop\Rachit\GST_format\Snapdeal\input_files\snapdeal_sales.xlsx"],
                    "user_email" : "rachit" ,
            }

ajio_payload = {"marketplace_name" : "ajio" ,
                "files": [
            r"C:\Users\st\Desktop\Rachit\GST_format\ajio\input_files\DropShipGstReports.xlsx",
            r"C:\Users\st\Desktop\Rachit\GST_format\ajio\input_files\DropShipRtvReports.xlsx"
        ],
                    "user_email" : "rachit" ,
            }

myntra_payload = {"marketplace_name" : "myntra" ,
                "files": [
            r"C:\Users\st\Desktop\Rachit\GST_format\myntra\Input_files\packed.csv",
            r"C:\Users\st\Desktop\Rachit\GST_format\myntra\Input_files\rt.csv",
            r"C:\Users\st\Desktop\Rachit\GST_format\myntra\Input_files\rto.csv"
        ],
                    "user_email" : "rachit" ,
            }

def platform(payload):
    marketplace_name = payload.get("marketplace_name")
    user_email = payload.get("user_email")
    files = payload.get("files")
    
    
    if marketplace_name == "meesho":
        if len(files) == 2:
            meesho_handler(payload=payload)
        else:
            return "Files missing"
    elif marketplace_name == "limeroad":
        if len(files) == 1:
            limeroad_handler(payload=payload)
        else:
            return "Files missing"
    elif marketplace_name == "flipcart":
        if len(files) == 1:
            flipcart_handler(payload=payload)
        else:
            return "Files missing"
    elif marketplace_name == "snapdeal":
        if len(files) == 1:
            snapdeal_handler(payload=payload)
    elif marketplace_name == "ajio":
        if len(files) == 2:
            ajio_handler(payload=payload)
    elif marketplace_name == "myntra":
        if len(files) == 3:
            myntra_handler(payload)
            
platform(payload=myntra_payload)
        
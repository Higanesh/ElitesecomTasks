from celery_app import run_myntra_gstr1, run_limeroad_gstr1, run_ajio_gstr1


if __name__ == "__main__":
    # --------- Myntra Task ---------
    task1 = run_myntra_gstr1.apply_async(
        args=[
            r"C:\ganesh\ElitesecomTasks\GSTR_1\gstr_1 test files\myntra\packed.csv",
            r"C:\ganesh\ElitesecomTasks\GSTR_1\gstr_1 test files\myntra\rt.csv",
            r"C:\ganesh\ElitesecomTasks\GSTR_1\gstr_1 test files\myntra\rto.csv",
            r"C:\ganesh\ElitesecomTasks\GSTR_1\gstr_1 test files\myntra\myntra_gstr1.xlsx",
        ],
        queue="myntra_queue"
    )
    print(f"📌 Myntra Task Sent! ID = {task1.id}")

    # --------- Limeroad Task ---------
    task2 = run_limeroad_gstr1.apply_async(
        args=[
            r"C:\ganesh\ElitesecomTasks\GSTR_1\gstr_1 test files\limeroad\limeroad_report.xlsx",
            r"C:\ganesh\ElitesecomTasks\GSTR_1\gstr_1 test files\limeroad\limeroad_gstr1.xlsx",
        ],
        queue="limeroad_queue"
    )
    print(f"📌 Limeroad Task Sent! ID = {task2.id}")

    # --------- Ajio Task ---------
    task3 = run_ajio_gstr1.apply_async(
        args=[
            r"C:\ganesh\ElitesecomTasks\GSTR_1\gstr_1 test files\ajio\DropShipGstReports.xlsx",
            r"C:\ganesh\ElitesecomTasks\GSTR_1\gstr_1 test files\ajio\DropShipRtvReports.xlsx",
            r"C:\ganesh\ElitesecomTasks\GSTR_1\gstr_1 test files\ajio\ajio_gstr1.xlsx",
        ],
        queue="ajio_queue"
    )
    print(f"📌 Ajio Task Sent! ID = {task3.id}")

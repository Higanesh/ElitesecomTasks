# main.py
from celery_app import add, subtract, multiply, divide

if __name__ == "__main__":
    print("Sending tasks...")
    r1 = add.delay(4, 6)         # -> add_queue
    r2 = subtract.delay(10, 4)    # -> subtract_queue
    r3 = multiply.delay(6, 7)     # -> multiply_queue
    r4 = divide.delay(20, 5)      # -> divide_queue

    print("Sent. IDs:")
    print(" add:", r1.id)
    print(" sub:", r2.id)
    print(" mul:", r3.id)
    print(" div:", r4.id)

    # Safest way to fetch (gives real traceback if task fails)
    print("Results:")
    print(" add:", r1.get(timeout=30, propagate=True))
    print(" sub:", r2.get(timeout=30, propagate=True))
    print(" mul:", r3.get(timeout=30, propagate=True))
    print(" div:", r4.get(timeout=30, propagate=True))

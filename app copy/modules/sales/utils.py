from datetime import datetime



def generate_invoice_number():
    return f"INV-{datetime.now().timestamp()}"
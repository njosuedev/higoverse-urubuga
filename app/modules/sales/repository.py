sales_db = []


def create_sale_repository(data):
    sales_db.append(data)
    return data



def get_sales_repository():
    return sales_db
import re
import json
from datetime import datetime, timedelta
import uuid


def log_function_call(func):
    """
    Decorator to log function calls.
    """
    def wrapper(*args, **kwargs):
        write_data = dict()
        call_string = f"Calling {func.__name__} with args: {args} and kwargs: {kwargs}"
        result = func(*args, **kwargs)
        response_string = f"{func.__name__} returned: {result}"

        request_id = str(uuid.uuid4())
        write_data[request_id] = {"call_string":call_string,"response_string":response_string}

        today_date = datetime.now().strftime("%Y-%m-%d")
        filename = f"history_{today_date}.json"
        with open(filename,"a") as f:
            json.dump(write_data, f, indent=4)
            f.write("\n")
        return result
    return wrapper


def remove_special_characters(s):
    return re.sub(r'[^A-Za-z0-9 ]+', '', s)

PRODUCTS = [
    {"id": 1, "name": "floral skirt", "color": "Pink", "price": 35, "size": "S", "in_stock": True, "site": "SiteA"},
    {"id": 2, "name": "white sneakers", "color": "white", "price": 65, "size": "8", "in_stock": True, "site": "SiteB"},
    {"id": 3, "name": "casual denim jacket", "color": "Blue", "price": 80, "size": "M", "in_stock": True, "site": "SiteC"},
    {"id": 4, "name": "cocktail dress", "color": "Black", "price": 120, "size": "L", "in_stock": False, "site": "SiteD"},
    {"id": 5, "name": "floral skirt", "color": "Red", "price": 40, "size": "M", "in_stock": True, "site": "SiteE"},
]

SHIPPING_DETAILS = {
    "SiteA": {"cost": 5.99, "delivery_days": 3},
    "SiteB": {"cost": 7.99, "delivery_days": 2},
    "SiteC": {"cost": 6.49, "delivery_days": 4},
    "SiteD": {"cost": 8.99, "delivery_days": 5},
    "SiteE": {"cost": 4.99, "delivery_days": 3},
}

RETURN_POLICIES = {
    "SiteA": "30-day return policy",
    "SiteB": "Hassle-free returns within 14 days",
    "SiteC": "No returns on sale items",
    "SiteD": "Free returns within 30 days",
    "SiteE": "Returns accepted within 7 days",
}

COMPETITOR_PRICES = {
    "floral skirt": {"SiteA": 35, "SiteB": 38, "SiteC": 40},
    "white sneakers": {"SiteA": 65, "SiteB": 60, "SiteC": 70},
    "casual denim jacket": {"SiteA": 80, "SiteB": 75, "SiteC": 85},
    "cocktail dress": {"SiteA": 120, "SiteB": 110, "SiteC": 130},
}

DISCOUNT_CODES = {
    "SAVE10": 0.10,  # 10% discount
    "FLASH20": 0.20,  # 20% discount
    "WINTERS15": 0.15,  # 15% discount
}

@log_function_call
def search_products(name=None, color=None, price_range=None, size=None):
    """
    Search for products based on user criteria.
    """
    name = remove_special_characters(name)
    results = []
    for product in PRODUCTS:
        if (not name or product["name"].lower() == name.lower()) and \
           (not color or product["color"].lower() == color.lower()) and \
           (not price_range or product["price"] <= price_range) and \
           (not size or product["size"].lower() == size.lower()):
            results.append(product)
    print(f"Search_product '{name}' results:", results)
    return results


@log_function_call
def estimate_shipping(product_name, delivery_date):
    """
    Estimate shipping feasibility, cost, and delivery date.
    """
    product_name = remove_special_characters(product_name)
    product = next((p for p in PRODUCTS if p["name"].lower() == product_name.lower()), None)
    if not product:
        return {"error": "Product not found."}
    
    site = product["site"]
    shipping_info = SHIPPING_DETAILS.get(site, {})
    if not shipping_info:
        return {"error": "Shipping details not available for this site."}
    
    today = datetime.now()
    delivery_days = shipping_info["delivery_days"]
    estimated_delivery = today + timedelta(days=delivery_days)
    
    user_delivery_date = datetime.strptime(delivery_date, "%Y-%m-%d")
    feasible = estimated_delivery <= user_delivery_date
    
    return {
        "feasible": feasible,
        "cost": shipping_info["cost"],
        "estimated_delivery": estimated_delivery.strftime("%Y-%m-%d"),
    }

@log_function_call
def apply_discount(base_price, promo_code):
    """
    Apply a discount code to adjust the price.
    """
    discount = DISCOUNT_CODES.get(promo_code, 0)
    discounted_price = base_price * (1 - discount)
    return {
        "original_price": base_price,
        "discounted_price": discounted_price,
        "discount_applied": discount * 100,
    }

@log_function_call
def compare_prices(product_name):
    """
    Compare prices of a product across competitors.
    """
    product_name = remove_special_characters(product_name)
    print("comapre prices output,",COMPETITOR_PRICES.get(product_name.lower(), {}))
    return COMPETITOR_PRICES.get(product_name.lower(), {})

@log_function_call
def check_return_policy(site):
    """
    Provide return policy details for a specific site.
    """
    return RETURN_POLICIES.get(site, "Return policy not found.")


@log_function_call
def notify_availability(product_name, email):
    """
    Simulate notifying the user when a product is back in stock.
    """
    product_name = remove_special_characters(product_name)
    product = next((p for p in PRODUCTS if p["name"].lower() == product_name.lower()), None)
    if not product:
        return {"error": "Product not found."}
    
    if product["in_stock"]:
        return {"message": f"{product_name} is already in stock."}
    else:
        import time
        time.sleep(5)
        return {"message": f"Notification sent to {email}: {product_name} is back in stock!"}
    

@log_function_call
def validate_email(email):
    """
    Validate an email address using regular expressions.
    """
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None


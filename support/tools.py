# support/tools.py


ORDERS = {
    "ORD-101": {
        "customer_name": "Priya Sharma",
        "product": "Vitamin C Serum (30ml)",
        "amount": "₹699",
        "status": "Out for Delivery",
        "courier": "BlueDart",
        "tracking_id": "BD-982103",
        "expected": "Expected by 6 PM today",
    },

    "ORD-102": {
        "customer_name": "Rahul Verma",
        "product": "Hydrating Sunscreen SPF 50",
        "amount": "₹499",
        "status": "Delivered",
        "courier": "Delhivery",
        "tracking_id": "DL-441029",
        "expected": "Delivered 14 days ago",
    },

    "ORD-103": {
        "customer_name": "Ananya Patel",
        "product": "Green Tea Face Wash + Toner",
        "amount": "₹850",
        "status": "Processing",
        "courier": "",
        "tracking_id": "",
        "expected": "Ordered 3 hours ago. Eligible for cancellation.",
    },
}


def get_order_details(order_id):

    order_id = order_id.upper().strip()

    order = ORDERS.get(order_id)

    if not order:

        return {
            "success": False,
            "message": "I couldn't find that order ID. Please check the order ID and try again."
        }

    return {
        "success": True,
        "order_id": order_id,
        "order": order
    }
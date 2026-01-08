from tnt_mart_tools import TnTMartTools

customer_id = 1
product_id = 16
quantity = 2
unit_price = 19.99


def test_add_to_cart():
    result = TnTMartTools.add_to_cart(customer_id=customer_id, product_id=product_id, quantity=quantity, unit_price=unit_price)
    
    #print the result for debugging nicely
    print(f"Result from add_to_cart: {result}")
    assert f"Product {product_id} added to cart for customer {customer_id}." in result
    
def test_remove_from_cart():
    result = TnTMartTools.remove_from_cart(customer_id=customer_id, product_id=product_id)
    
    #print the result for debugging nicely
    print(f"Result from remove_from_cart: {result}")
    assert f"Product {product_id} removed from cart for customer {customer_id}." in result

def test_update_quantity_in_cart():
    new_quantity = 5
    result = TnTMartTools.update_quantity_in_cart(quantity=new_quantity, customer_id=customer_id, product_id=product_id)
    
    #print the result for debugging nicely
    print(f"Result from update_quantity_in_cart: {result}")
    
    assert f"Quantity of product {product_id} updated to {new_quantity} for customer {customer_id}." in result

def test_approve_refund():
    refund_id = 1
    result = TnTMartTools.approve_refund(refund_id)
    
    #print the result for debugging nicely
    print(f"Result from approve_refund: {result}")
    
    assert f"Refund request with ID {refund_id} has been approved." in result

def test_reject_refund():   
    refund_id = 2
    reason = "Item not eligible for refund"
    result = TnTMartTools.reject_refund(refund_id, reason)
    
    #print the result for debugging nicely
    print(f"Result from reject_refund: {result}")
    
    assert f"Refund request with ID {refund_id} has been rejected for reason: {reason}" in result  

def test_getETA():
    location = "Local"
    result = TnTMartTools.getETA(location)
    
    #print the result for debugging nicely
    print(f"Result from getETA: {result}")
    
    assert "ETA is 5 days" in result


if __name__ == "__main__":
    TnTMartTools.create_connection()
    test_add_to_cart()
    test_update_quantity_in_cart()
    test_remove_from_cart()
    test_approve_refund()
    test_reject_refund()
    test_getETA()
    
    print("All tests passed.")
    TnTMartTools.close_connection()
    
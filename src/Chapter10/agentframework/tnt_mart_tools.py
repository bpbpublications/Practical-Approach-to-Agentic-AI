"""
This module implements a set of custom plugins for the TNT Mart application using the Semantic Kernel framework.
This includes functions for Shopping Cart updates, Refund Management, and Order Processing.

Key Functions:
- add_to_cart: Adds an item to the shopping cart.
- remove_from_cart: Removes an item from the shopping cart.
- update_quantity_in_cart: Updates the quantity of an item in the shopping cart.
- approve_refund: Approves a refund request.
- reject_refund: Rejects a refund request.

"""

from agent_framework import ai_function
from dotenv import load_dotenv
import os, json, psycopg2, pathlib
from psycopg2.extras import RealDictCursor
from typing import Annotated
from decimal import Decimal

class TnTMartTools:
    connection = None
    cursor = None

    @staticmethod
    @ai_function(name="create_connection", description="Create a connection object to the postgres database.")
    def create_connection():
        # Load environment variables from .env file
        current_dir = pathlib.Path(__file__).parent
        env_path = current_dir / ".env"
        load_dotenv(dotenv_path=env_path)
        print("create_connection function called... ")
        TnTMartTools.connection = psycopg2.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT")
        )
        TnTMartTools.cursor = TnTMartTools.connection.cursor(cursor_factory=RealDictCursor)
            
    @staticmethod
    @ai_function(name="close_connection", description="Closes the connection to the database.")
    def close_connection() -> Annotated[str, "Returns a message indicating the status of the connection closure."]:
        """
        Closes the connection to the PostgreSQL database.

        :return: Message indicating the status of the connection closure.
        :rtype: str
        """
        print("close_connection function called... ")
        try:
            if TnTMartTools.connection:
                TnTMartTools.cursor.close()
                TnTMartTools.connection.close()
            return "Connection closed successfully."
        except Exception as e:
            return str(e)
        
    @staticmethod
    @ai_function(description="Adds an item to the shopping cart.", name="add_to_cart")    
    def add_to_cart(customer_id: int, product_id: int, quantity: int, unit_price: float) -> str:
        """
        Adds an item to the shopping cart.
        Args:
            customer_id (int): The ID of the customer.
            product_id (int): The ID of the product to add.
            quantity (int): The quantity of the product.
            unit_price (float): The unit price of the product.
        Returns:
            str: A message indicating whether the item was added successfully.
        """
        
        print(f"Adding product {product_id} to cart for customer {customer_id} with quantity {quantity} at price {unit_price}.")
        
        query = f"""insert into shopping_cart (customer_id, product_id, quantity, unit_price) values ({customer_id}, {product_id}, {quantity}, {unit_price});"""
        cursor = TnTMartTools.connection.cursor()
        cursor.execute(query)
        TnTMartTools.connection.commit()
        
        return f"Product {product_id} added to cart for customer {customer_id}."

    @staticmethod
    @ai_function(description="Removes an item from the shopping cart.", name="remove_from_cart")
    def remove_from_cart(customer_id: int, product_id: int) -> str:
        """
        Removes an item from the shopping cart.
        Args:
            customer_id (int): The ID of the customer.
            product_id (int): The ID of the product to remove.
        Returns:
            str: A message indicating whether the item was removed successfully.
        """
        print(f"Removing product {product_id} from cart for customer {customer_id}.")

        query = f"""delete from shopping_cart where customer_id={customer_id} and product_id={product_id};"""
        cursor = TnTMartTools.connection.cursor()
        cursor.execute(query)
        TnTMartTools.connection.commit()

        return f"Product {product_id} removed from cart for customer {customer_id}."

    @staticmethod
    @ai_function(description="Updates the quantity of an item in the shopping cart.", name="update_quantity_in_cart")
    def update_quantity_in_cart(quantity: int, customer_id: int, product_id: int) -> str:
        """
        Updates the quantity of an item in the shopping cart.
        Args:
            quantity (int): The new quantity of the product.
            customer_id (int): The ID of the customer.
            product_id (int): The ID of the product to update.
        Returns:
            str: A message indicating whether the quantity was updated successfully.
        """
        print(f"Updating quantity of product {product_id} to {quantity} for customer {customer_id}.")

        query = f"""update shopping_cart set quantity={quantity} where customer_id={customer_id} and product_id={product_id};"""
        cursor = TnTMartTools.connection.cursor()
        cursor.execute(query)
        TnTMartTools.connection.commit()

        return f"Quantity of product {product_id} updated to {quantity} for customer {customer_id}."

    @staticmethod
    @ai_function(description="Approves a refund request.", name="approve_refund")
    def approve_refund(refund_id: int) -> str:
        """
        Approves a refund request.
        Args:
            refund_id (int): The ID of the refund to approve.
        Returns:
            str: A message indicating whether the refund was approved successfully.
        """
        print(f"Approving refund request with ID {refund_id}.")

        query = f"""update refund set status='Approved' where refund_id={refund_id};"""
        cursor = TnTMartTools.connection.cursor()
        cursor.execute(query)
        TnTMartTools.connection.commit()

        return f"Refund request with ID {refund_id} has been approved." 
    
    @staticmethod
    @ai_function(description="Rejects a refund request.", name="reject_refund")
    def reject_refund(refund_id: int, reason: str) -> str:
        """
        Rejects a refund request.
        Args:
            refund_id (int): The ID of the refund to reject.
            reason (str): The reason for rejecting the refund.
        Returns:
            str: A message indicating whether the refund was rejected successfully.
        """
        print(f"Rejecting refund request with ID {refund_id} for reason: {reason}")

        query = f"""update refund set status='Rejected', reason='{reason}' where refund_id={refund_id};"""
        cursor = TnTMartTools.connection.cursor()
        cursor.execute(query)
        TnTMartTools.connection.commit()

        return f"Refund request with ID {refund_id} has been rejected for reason: {reason}"
    
    @staticmethod
    @ai_function(description="Provides ETA for dispatched orders.", name="getETA")
    def getETA(location:str) -> str:
        """Get the ETA for Dispatched orders."""
        # Simulate investigating a locked card
        print("Determining ETA Dispatched order from  warehouse")
        if location == "Local":
            return "ETA is 5 days"
        else:
            return "ETA is 10 days"


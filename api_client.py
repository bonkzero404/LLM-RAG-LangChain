import requests
from typing import Any
from config import API_URL

def api_create_order(order_data: Any) -> (Any | dict[str, Any]):
    response = requests.post(f"{API_URL}/orders", json=order_data)
    return response.json() if response.status_code < 400 else {"error": response.json()}

def api_get_list_product() -> (Any | dict[str, Any]):
    response = requests.get(f"{API_URL}/products")
    return response.json()

def api_search_product(query: str) -> (Any | dict[str, Any]):
    response = requests.get(f"{API_URL}/products/?query={query}")
    return response.json()

def api_check_order(order_number: str) -> (Any | dict[str, Any]):
    response = requests.get(f"{API_URL}/orders/{order_number}")
    return response.json() if response.status_code < 400 else {"error": response.json()}

def api_report_order(year: str) -> (Any | dict[str, Any]):
    response = requests.get(f"{API_URL}/order-report?year={year}")
    return response.json() if response.status_code < 400 else {"error": response.json()}
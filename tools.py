import matplotlib.pyplot as plt
import os
from typing import Any
from pydantic import BaseModel, Field
from langchain.tools import tool
from vector_store_documents import VectorStoreDocuments
from api_client import api_create_order, api_get_list_product, api_search_product, api_check_order, api_report_order
from config import API_URL

@tool("get-list-product-tool")
def get_list_products():
    """ Daftar produk dan harga yang tersedia, jelaskan jika ada yang bertanya spesifik tentang harga produk atau layanan yang tersedia. """
    response = api_get_list_product()
    return response

class GetProductRequest(BaseModel):
    search: str = Field(description="Kata kunci untuk mencari produk atau layanan, bisa berupa nama produk atau SKU, jika pengguna belum mengetahui SKU, maka tanyakan terlebih dahulu dan berikan daftar produk")

@tool("get-product-tool", args_schema=GetProductRequest)
def get_product(search):
    """ Mendapatkan informasi daftar harga dari layanan atau produk, hasil harus menampilkan SKU, Nama dan Harga, dalam hal ini produk bisa di sebut juga sebagai layanan"""
    response = api_search_product(search)
    product_text = "\n".join(f"SKU: {prod['sku']}, Nama: {prod['name']}, Harga: {prod['price']}" for prod in response)
    return product_text

class GetOrderRequest(BaseModel):
    sku: str = Field(description="SKU harus diisi, SKU adalah kode unik untuk produk, SKU bisa dilihat di daftar produk, jika pengguna belum mengetahui SKU, maka tanyakan terlebih dahulu dan berikan daftar produk, jika customer memberikan nama produk, maka lihat nama produk tersebut di daftar produk untuk mendapatkan SKU")
    email: str = Field(description="Email customer harus diisi, jika customer belum menyebutkan email, maka tanyakan terlebih dahulu")
    full_name: str = Field(description="Nama lengkap customer, jika customer belum menyebutkan nama, maka tanyakan terlebih dahulu")

@tool("create-order-tool", args_schema=GetOrderRequest)
def create_order(sku, email, full_name):
    """ Membuat order baru, hasil harus menampilkan nomor order dan link pembayaran, jika ada error maka tampilkan pesan terkait error tersebut, jika customer telah menyebutkan nama, maka gunakan nama tersebut untuk mengisi data order, jika pengguna belum menyebutkan email atau nama, maka tanya terlebih dahulu emailnya"""
    response = api_create_order({"sku": sku, "email": email, "full_name": full_name})
    if "error" in response:
        return f"Error: {response['error']}, try again"
    return f"Order Number: {response['order_number']} created. Payment link: {response['invoice_url']}"

class GetCheckOrderRequest(BaseModel):
    order_number: str = Field(description="Nomor order harus diisi, nomor order bisa dilihat di invoice yang diberikan saat pembuatan order")

@tool("check-order-tool", args_schema=GetCheckOrderRequest)
def check_order(order_number):
    """ Memeriksa order berdasarkan nomor order, cek berdasarkan payment_status, jika order telah selesai maka tampilkan status selesai, jika order belum selesai maka tampilkan status pending, jika order tidak ditemukan maka tampilkan pesan order tidak ditemukan, Jika customer sudah merasa membayar namun status masih pending, maka berikan nomor telepon JuraganKlod untuk konfirmasi pembayaran"""
    response = api_check_order(order_number)
    if "error" in response:
        return f"Error: {response['error']}, try again"

    status = response['payment_status']
    if status == "pending":
        return f"Status: {status}. Please complete payment soon."
    return f"Status: {status}. Thank you for your payment."

class OrderReportRequest(BaseModel):
    year: int = Field(description="Tahun laporan order harus diisi, laporan order berdasarkan tahun")

@tool("order-report-tool", args_schema=OrderReportRequest)
def order_report(year: int):
    """Membuat grafik laporan order per tahun, hasil berisi grafik bar chart yang menampilkan jumlah order per bulan, hasilnya adalah markdown image"""
    response = api_report_order(year)
    if "error" in response:
        return f"Error: {response['error']}, try again"

    months = response['months']
    order_counts = response['order_counts']

    # Buat plot dengan Matplotlib
    plt.figure(figsize=(10, 6))
    plt.bar(months, order_counts, color='blue', alpha=0.7)

    plt.title(f'Order Report for {year}')
    plt.xlabel('Month')
    plt.ylabel('Number of Orders')
    plt.xticks(rotation=45)
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    # Simpan gambar
    os.makedirs("storages/reports", exist_ok=True)
    report_filename = f"order_report_{year}.png"
    report_path = f"storages/reports/{report_filename}"
    plt.savefig(report_path, bbox_inches='tight')
    plt.close()

    return f"{API_URL}/storages/reports/{report_filename}"

class GetContentInformation(BaseModel):
    query: str = Field(description="Query yang ingin dicari, bisa berupa nama layanan, produk, tentang perusahaan atau informasi lainnya")

@tool("get-content-tool", args_schema=GetContentInformation)
def get_content(query: str):
    """Mendapatkan informasi dari konten yang tersedia, berupa layanan, produk, atau informasi lainnya, gunakan tool ini jika jawaban tidak ditemukan dari tool lainnya"""
    store = VectorStoreDocuments()
    retrieved_docs = store.vector_store().retriever().invoke(input=query, k=2)

    if not retrieved_docs:
        return "Maaf, tidak ada informasi yang ditemukan terkait."

    print("Retrieved docs:", retrieved_docs)

    processed_docs = []
    for doc in retrieved_docs:
        content = doc.page_content.strip()
        if content:
            processed_docs.append(content)

    result = "\n\n".join(processed_docs)

    return result

def run_tool():
    tools = [get_content, get_list_products, get_product, create_order, check_order, order_report]
    return tools
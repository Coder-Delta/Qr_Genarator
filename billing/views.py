from django.shortcuts import render
from django.http import FileResponse
import qrcode
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import os
from io import BytesIO
import requests

ETHERSCAN_API_KEY = "YourEtherscanAPIKey"
ETHERSCAN_URL = "https://api.etherscan.io/api"

def fetch_blockchain_data(tx_hash):
    """Fetch real transaction details from Ethereum blockchain"""
    url = f"{ETHERSCAN_URL}?module=proxy&action=eth_getTransactionByHash&txhash={tx_hash}&apikey={ETHERSCAN_API_KEY}"
    response = requests.get(url)
    data = response.json()

    if "result" in data and data["result"]:
        tx = data["result"]
        from_addr = tx["from"]
        to_addr = tx["to"]
        value_wei = int(tx["value"], 16)
        value_eth = value_wei / 10**18

        return {
            "transaction_hash": tx_hash,
            "from_wallet": from_addr,
            "to_wallet": to_addr,
            "amount": value_eth,
            "status": "Confirmed"
        }
    
    return {
        "transaction_hash": tx_hash,
        "from_wallet": "N/A",
        "to_wallet": "N/A",
        "amount": 0,
        "status": "Not Found"
    }
def generate_invoice_pdf(data):
    # Generate QR Code
    qr = qrcode.QRCode(version=1, box_size=8, border=3)
    qr.add_data(f"TX: {data['transaction_hash']} | Amount: {data['amount']}")
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="blue", back_color="white")
    qr_path = f"billing/static/invoices/{data['transaction_hash']}.png"
    os.makedirs(os.path.dirname(qr_path), exist_ok=True)
    qr_img.save(qr_path)

    # Generate PDF in memory
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Header
    c.setFont("Helvetica-Bold", 20)
    c.drawString(200, 800, "BLOCKCHAIN INVOICE")

    # Invoice details
    c.setFont("Helvetica", 12)
    c.drawString(50, 750, f"Transaction Hash: {data['transaction_hash']}")
    c.drawString(50, 730, f"From Wallet: {data['from_wallet']}")
    c.drawString(50, 710, f"To Wallet: {data['to_wallet']}")
    c.drawString(50, 690, f"Amount: {data['amount']} ETH")
    c.drawString(50, 670, f"Payment Status: {data['status']}")

    # QR Code
    c.drawImage(qr_path, 400, 620, width=150, height=150)

    # Footer
    c.setFont("Helvetica", 10)
    c.drawString(50, 100, "This invoice is auto-generated from the blockchain data.")
    c.drawString(50, 85, "Scan the QR code for transaction verification.")

    c.save()
    buffer.seek(0)
    return buffer

def index(request):
    return render(request, "billing/index.html")

def generate_invoice(request):
    if request.method == "POST":
        tx_hash = request.POST.get("tx_hash")
        data = fetch_blockchain_data(tx_hash)
        pdf_buffer = generate_invoice_pdf(data)
        return FileResponse(pdf_buffer, as_attachment=True, filename=f"invoice_{tx_hash}.pdf")
    return render(request, "billing/index.html")

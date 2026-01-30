from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import datetime, os, secrets
from security_utils import generate_order_id

# ================= FONT =================
FONT_PATH = os.path.join("fonts", "NotoSans-VariableFont_wdth,wght.ttf")
pdfmetrics.registerFont(TTFont("Noto", FONT_PATH))

# ================= FOLDER =================
INVOICE_FOLDER = "invoices"
os.makedirs(INVOICE_FOLDER, exist_ok=True)

# ================= THEMES =================
THEMES = [
 {"bg":"#f5f0e6","header":"#2c3e50","accent":"#c4d7c8"},
 {"bg":"#eef4ff","header":"#355c7d","accent":"#cde3ff"},
 {"bg":"#f1fff4","header":"#2d6a4f","accent":"#c8f7d2"},
 {"bg":"#fff4fb","header":"#6a4c93","accent":"#f1d4ff"},
 {"bg":"#fff9f0","header":"#8d5524","accent":"#ffe3c8"},
 {"bg":"#fff5f0","header":"#b56576","accent":"#ffd6d6"},
 {"bg":"#f0fff9","header":"#1b4332","accent":"#b7efc5"},
 {"bg":"#f3f0ff","header":"#5f0f40","accent":"#d0bdf4"},
 {"bg":"#fffce0","header":"#b08968","accent":"#ffe5b4"},
 {"bg":"#f0faff","header":"#0077b6","accent":"#caf0f8"},
]

# ================= MAIN FUNCTION =================
def create_invoice(order):

    order_id = generate_order_id()
    theme = THEMES[secrets.randbelow(len(THEMES))]
    path = f"{INVOICE_FOLDER}/{order_id}.pdf"

    c = canvas.Canvas(path, pagesize=A4)
    width, height = A4

    # ---------- BACKGROUND ----------
    c.setFillColor(HexColor(theme["bg"]))
    c.rect(0, 0, width, height, fill=1)

    # ---------- HEADER ----------
    c.setFillColor(HexColor(theme["header"]))
    c.rect(0, height - 120, width, 120, fill=1)

    c.setFillColor("#ffffff")
    c.setFont("Noto", 28)
    c.drawString(50, height - 70, "SAAC ONLINE")
    c.setFont("Noto", 14)
    c.drawString(50, height - 95, "Thank you for your order")

    # ---------- WATERMARK ----------
    c.setFillColor("#e8e8e8")
    c.setFont("Noto", 70)
    c.drawCentredString(width/2, height/2 + 60, "SAAC")

    # ---------- CUSTOMER INFO ----------
    y = height - 160
    c.setFillColor(HexColor(theme["header"]))
    c.setFont("Noto", 12)

    c.drawString(50, y, f"Order ID: {order_id}")
    c.drawString(50, y - 20, f"Date: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}")
    c.drawString(50, y - 40, f"Name: {order.get('name','-')}")
    c.drawString(50, y - 60, f"Phone: {order.get('phone','-')}")
    c.drawString(50, y - 80, f"Address: {order.get('address','-')}")


    # ---------- PRODUCTS TITLE ----------
    y -= 130
    c.setFont("Noto", 16)
    c.drawString(50, y, "Products")

    # ---------- TABLE HEADERS ----------
    y -= 20
    c.setFont("Noto", 12)
    c.setFillColor(HexColor(theme["header"]))
    c.drawString(60, y, "Product")
    c.drawRightString(350, y, "Quantity")
    c.drawRightString(520, y, "Amount")

    y -= 8
    c.setStrokeColor(HexColor(theme["header"]))
    c.line(50, y, width - 50, y)
    y -= 18

    # ---------- ITEMS ----------
    total = 0
    c.setFillColor("#000000")

    for item in order["items"]:
        item_total = item["price"] * item["qty"]
        total += item_total
        unit = item.get("unit", "kg")

        c.setFont("Noto", 12)
        c.drawString(60, y, item["name"])
        c.drawRightString(350, y, f"{item['qty']} {unit}")
        c.drawRightString(520, y, f"Rs {item_total}")

        y -= 22
        if y < 150:
            c.showPage()
            y = height - 100

    # ===== COURIER CHARGES (ONLY ADDITION) =====
    courier = order.get("courier", 0)
    if courier > 0:

        if y < 150:
            c.showPage()
            y = height - 100
            c.setFont("Noto", 12)

        c.setFont("Noto", 12)
        c.drawString(60, y, "Courier Charges")
        c.drawRightString(520, y, f"Rs {courier}")
        total += courier
        y -= 22


    # ---------- TOTAL ----------
    y -= 30
    c.setFillColor(HexColor(theme["accent"]))
    c.roundRect(370, y - 18, 150, 28, 8, fill=1)

    c.setFillColor("#000000")
    c.setFont("Noto", 13)
    c.drawRightString(510, y - 2, f"Total Rs {total}")

    # ---------- FOOTER ----------
    c.setFillColor("#555555")

    c.setFont("Noto", 12)
    c.drawCentredString(width/2, 65, "Mahalasa Home Products — Kundapura")

    c.setFont("Noto", 9)
    c.drawCentredString(
        width/2,
        48,
        "Thank you for your Business! We look forward to working with you again."
    )

    c.drawCentredString(width/2, 32, "Contact: +91 9448657267 | Instagram: @mahalasahomeproducts")
    c.drawCentredString(width/2, 18, "© 2026 Mahalasa Home Products")

    c.save()
    return order_id, path, total

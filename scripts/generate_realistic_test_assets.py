import io
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors

ROOT_DIR = Path(__file__).resolve().parent.parent
TARGET_DIR = ROOT_DIR / "demo" / "specs" / "samples" / "new_case"
TARGET_DIR.mkdir(parents=True, exist_ok=True)


def get_default_font(size: int = 14):
    try:
        # Try Windows standard fonts
        for font_name in ["segoeui.ttf", "arial.ttf", "tahoma.ttf", "calibri.ttf"]:
            font_path = Path("C:/Windows/Fonts") / font_name
            if font_path.exists():
                return ImageFont.truetype(str(font_path), size)
    except Exception:
        pass
    return ImageFont.load_default()


def generate_chat_screenshot():
    width, height = 800, 1050
    img = Image.new("RGB", (width, height), color=(17, 27, 33)) # WhatsApp dark background
    draw = ImageDraw.Draw(img)

    title_font = get_default_font(20)
    sub_font = get_default_font(13)
    msg_font = get_default_font(15)
    time_font = get_default_font(12)
    banner_font = get_default_font(13)

    # 1. Header Bar
    draw.rectangle([0, 0, width, 90], fill=(32, 44, 51))
    # Avatar Circle
    draw.ellipse([20, 15, 80, 75], fill=(0, 168, 132))
    draw.text((36, 32), "AE", fill=(255, 255, 255), font=title_font)
    # Name & Subtitle
    draw.text((95, 22), "Apex Electro Hub BD", fill=(233, 237, 239), font=title_font)
    draw.text((95, 52), "+880 1912-987654 • Business Account", fill=(134, 150, 160), font=sub_font)

    # Date header pill
    draw.rounded_rectangle([330, 110, 470, 138], radius=8, fill=(24, 34, 41))
    draw.text((352, 116), "22 October 2026", fill=(134, 150, 160), font=time_font)

    # Message 1 (Consumer - Outgoing Right)
    m1_top = 160
    draw.rounded_rectangle([180, m1_top, 770, m1_top + 130], radius=12, fill=(0, 92, 75))
    lines1 = [
        "Bhai, parcel peyechi (Invoice AEH-2026-9941). Apnara bolchilen",
        "Sony WH-1000XM4 original headphone with 1 year warranty,",
        "ami 18,500 BDT Nagad e advance disi. Kintu box khule dekhi duplicate",
        "replica item! Bluetooth pairing hoy na, warranty card-o nai.",
        "Please exchange ba 18,500 refund den.",
    ]
    for i, line in enumerate(lines1):
        draw.text((195, m1_top + 10 + i * 21), line, fill=(233, 237, 239), font=msg_font)
    draw.text((710, m1_top + 110), "02:48 PM ✓✓", fill=(83, 189, 235), font=time_font)

    # Message 2 (Merchant - Incoming Left)
    m2_top = 310
    draw.rounded_rectangle([30, m2_top, 620, m2_top + 95], radius=12, fill=(32, 44, 51))
    lines2 = [
        "Sale offer er item konovabei exchange ba return hoy na.",
        "Amader management policy te refund er kono option nai.",
        "Apnar product check korei pathano hoyeche.",
    ]
    for i, line in enumerate(lines2):
        draw.text((45, m2_top + 10 + i * 22), line, fill=(233, 237, 239), font=msg_font)
    draw.text((550, m2_top + 75), "02:52 PM", fill=(134, 150, 160), font=time_font)

    # Message 3 (Consumer - Outgoing Right)
    m3_top = 425
    draw.rounded_rectangle([220, m3_top, 770, m3_top + 115], radius=12, fill=(0, 92, 75))
    lines3 = [
        "Eta direct fraud! Apnar page e 1 year warranty lekha chilo.",
        "Ami 18,500 taka disi, eta genuine bole sell korsen.",
        "Ajker moddhe refund na dile ami DNCRP (ভোক্তা অধিকার) te",
        "Section 45 e case korbo.",
    ]
    for i, line in enumerate(lines3):
        draw.text((235, m3_top + 10 + i * 22), line, fill=(233, 237, 239), font=msg_font)
    draw.text((710, m3_top + 95), "02:55 PM ✓✓", fill=(83, 189, 235), font=time_font)

    # Message 4 (Merchant - Incoming Left)
    m4_top = 560
    draw.rounded_rectangle([30, m4_top, 500, m4_top + 75], radius=12, fill=(32, 44, 51))
    lines4 = [
        "Apnar jekhane iccha jan, amader kisu hobe na.",
        "Aro message dile block kore debo.",
    ]
    for i, line in enumerate(lines4):
        draw.text((45, m4_top + 10 + i * 22), line, fill=(233, 237, 239), font=msg_font)
    draw.text((430, m4_top + 55), "02:56 PM", fill=(134, 150, 160), font=time_font)

    # System Block Banner
    draw.rounded_rectangle([100, 680, 700, 740], radius=10, fill=(24, 34, 41))
    draw.text(
        (130, 700),
        "🚫 You can't reply to this conversation. You have been blocked by the merchant.",
        fill=(241, 90, 90),
        font=banner_font,
    )

    out_path = TARGET_DIR / "evidence_apex_chat_blocking.png"
    img.save(out_path, format="PNG")
    print(f"Generated realistic chat screenshot: {out_path} ({out_path.stat().st_size} bytes)")


def generate_nagad_payment_slip():
    width, height = 650, 920
    img = Image.new("RGB", (width, height), color=(248, 249, 250))
    draw = ImageDraw.Draw(img)

    header_font = get_default_font(22)
    amount_font = get_default_font(36)
    label_font = get_default_font(14)
    val_font = get_default_font(15)

    # 1. Header Banner (Nagad Orange)
    draw.rectangle([0, 0, width, 140], fill=(238, 59, 36))
    draw.text((220, 35), "Nagad Payment", fill=(255, 255, 255), font=header_font)
    draw.text((245, 75), "Merchant Payment Successful", fill=(255, 240, 240), font=label_font)

    # 2. Main Card
    draw.rounded_rectangle([30, 110, width - 30, height - 60], radius=16, fill=(255, 255, 255), outline=(222, 226, 230), width=1)

    # Checkmark circle
    draw.ellipse([275, 140, 375, 240], fill=(40, 167, 69))
    draw.text((310, 165), "✓", fill=(255, 255, 255), font=amount_font)

    # Amount
    draw.text((215, 260), "18,500.00 BDT", fill=(33, 37, 41), font=amount_font)
    draw.text((260, 310), "Paid In Full", fill=(108, 117, 125), font=label_font)

    draw.line([60, 345, width - 60, 345], fill=(233, 236, 239), width=1)

    # Data Rows
    rows = [
        ("Merchant Name", "Apex Electro Hub BD"),
        ("Merchant Account", "01912987654 (Nagad Merchant)"),
        ("Transaction ID (TrxID)", "9KA7X2P41M"),
        ("Invoice Reference", "AEH-2026-9941"),
        ("Customer Name", "Tanvir Ahmed"),
        ("Customer Number", "01812345678"),
        ("Date & Time", "22 Oct 2026, 02:45 PM"),
        ("Convenience Fee", "0.00 BDT"),
        ("Total Debited", "18,500.00 BDT"),
    ]

    curr_y = 370
    for label, val in rows:
        draw.text((60, curr_y), label, fill=(108, 117, 125), font=label_font)
        draw.text((300, curr_y), val, fill=(33, 37, 41), font=val_font)
        curr_y += 44

    # Bottom Seal
    draw.text((170, curr_y + 30), "Verified Electronic MFS Transaction Record", fill=(40, 167, 69), font=label_font)

    out_path = TARGET_DIR / "evidence_nagad_payment_slip.png"
    img.save(out_path, format="PNG")
    print(f"Generated realistic Nagad payment slip: {out_path} ({out_path.stat().st_size} bytes)")


def generate_invoice_pdf():
    out_path = TARGET_DIR / "evidence_order_invoice_nagad.pdf"
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    width, height = letter

    # Header
    c.setFont("Helvetica-Bold", 18)
    c.setFillColor(colors.HexColor("#1A365D"))
    c.drawString(50, height - 60, "APEX ELECTRO HUB BD")
    
    c.setFont("Helvetica", 10)
    c.setFillColor(colors.HexColor("#4A5568"))
    c.drawString(50, height - 76, "Shop 412, Multiplan Center, Elephant Road, Dhaka-1205")
    c.drawString(50, height - 90, "BIN: 002910482-0101 | Contact: +880 1912-987654")

    c.setFont("Helvetica-Bold", 16)
    c.setFillColor(colors.HexColor("#2B6CB0"))
    c.drawRightString(width - 50, height - 60, "COMMERCIAL SALES INVOICE")
    
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(colors.HexColor("#2D3748"))
    c.drawRightString(width - 50, height - 78, "Invoice #: AEH-2026-9941")
    c.drawRightString(width - 50, height - 92, "Date: 22 October 2026")
    c.drawRightString(width - 50, height - 106, "Delivery Note: REDX-8829104")

    c.setStrokeColor(colors.HexColor("#CBD5E0"))
    c.line(50, height - 120, width - 50, height - 120)

    # Bill To
    c.setFont("Helvetica-Bold", 11)
    c.drawString(50, height - 140, "BILL TO & RECIPIENT:")
    c.setFont("Helvetica", 10)
    c.drawString(50, height - 156, "Tanvir Ahmed")
    c.drawString(50, height - 170, "House 14, Road 7, Sector 4, Uttara, Dhaka-1230")
    c.drawString(50, height - 184, "Phone: +880 1812-345678 | Email: tanvir.ahmed@example.com")

    # Order Meta Table
    c.setFillColor(colors.HexColor("#EDF2F7"))
    c.rect(50, height - 235, width - 100, 25, fill=1, stroke=0)
    c.setFillColor(colors.HexColor("#2D3748"))
    c.setFont("Helvetica-Bold", 10)
    c.drawString(60, height - 225, "ITEM DESCRIPTION & SPECIFICATION")
    c.drawString(340, height - 225, "WARRANTY")
    c.drawString(440, height - 225, "QTY")
    c.drawRightString(width - 60, height - 225, "AMOUNT (BDT)")

    # Item Row
    c.setFont("Helvetica-Bold", 10)
    c.drawString(60, height - 255, "Sony WH-1000XM4 Wireless Noise-Cancelling Headphones")
    c.setFont("Helvetica", 9)
    c.setFillColor(colors.HexColor("#718096"))
    c.drawString(60, height - 270, "Color: Black | S/N: SN-WH4-998821 | Certified Brand New")
    c.setFillColor(colors.HexColor("#2D3748"))
    c.drawString(340, height - 255, "12 Months Official")
    c.drawString(445, height - 255, "1")
    c.setFont("Helvetica-Bold", 10)
    c.drawRightString(width - 60, height - 255, "18,500.00 BDT")

    c.line(50, height - 285, width - 50, height - 285)

    # Subtotals & Payment Info
    c.setFont("Helvetica", 10)
    c.drawString(60, height - 310, "Subtotal:")
    c.drawRightString(width - 60, height - 310, "18,500.00 BDT")
    c.drawString(60, height - 325, "Courier Shipping (RedX Express):")
    c.drawRightString(width - 60, height - 325, "0.00 BDT (Free Promo)")
    
    c.setFont("Helvetica-Bold", 11)
    c.drawString(60, height - 345, "Total Invoiced Amount:")
    c.drawRightString(width - 60, height - 345, "18,500.00 BDT")

    # Payment Confirmation Box
    c.setFillColor(colors.HexColor("#F0FFF4"))
    c.rect(50, height - 425, width - 100, 65, fill=1, stroke=1)
    c.setFillColor(colors.HexColor("#22543D"))
    c.setFont("Helvetica-Bold", 11)
    c.drawString(65, height - 380, "PAYMENT STATUS: PAID IN ADVANCE VIA NAGAD MFS")
    c.setFont("Helvetica", 10)
    c.drawString(65, height - 398, "Nagad TrxID: 9KA7X2P41M | Merchant Wallet: 01912987654 | Amount: 18,500.00 BDT")
    c.drawString(65, height - 414, "Paid Date: 22 October 2026, 02:45 PM | Verification Code: PAID-OK-8841")

    # Statutory Declaration
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(colors.HexColor("#2D3748"))
    c.drawString(50, height - 460, "STATUTORY CONSUMER GUARANTEE & INVARIANTS:")
    c.setFont("Helvetica", 8)
    c.setFillColor(colors.HexColor("#718096"))
    c.drawString(50, height - 475, "This commercial invoice is issued under the Bangladesh Consumer Rights Protection Act 2009 (CRPA).")
    c.drawString(50, height - 487, "Goods sold are warranted genuine and defect-free. False descriptions constitute actionable violations under Section 45.")
    c.drawString(50, height - 499, "Dispute procedural jurisdiction: Directorate of National Consumers' Right Protection (DNCRP), Dhaka.")

    c.showPage()
    c.save()

    with open(out_path, "wb") as f:
        f.write(buf.getvalue())
    print(f"Generated realistic PDF invoice: {out_path} ({out_path.stat().st_size} bytes)")


if __name__ == "__main__":
    generate_chat_screenshot()
    generate_nagad_payment_slip()
    generate_invoice_pdf()
    print("All realistic test assets created successfully.")


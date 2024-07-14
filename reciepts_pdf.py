from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.colors import Color
import arabic_reshaper
from bidi.algorithm import get_display
from datetime import datetime
from reportlab.lib.pagesizes import letter
from database import SessionLocal
from models import Order, Customer

session = SessionLocal()


def get_inventory(id):
    orders = session.query(Order).filter_by(id=id).all()
    items = []
    for order in orders:
        for item in order.items:
            items.append(item)
    return items


class Product:
    def __init__(self, items):
        self.items = items
        self.total = 0
        self.total_no_tax = 0
        self.total_tax = 0
        self.quantity = 0
        self.calculate()

    def calculate(self):
        for item in self.items:
            self.total_no_tax += item.inventory.price
            self.total_tax += item.inventory.price*.15
            self.total = + self.total_no_tax+self.total_tax
            self.quantity += item.quantity


class CreatePdf:
    id = []

    def __init__(self, output_file):
        self.output_file = output_file
        self.c = canvas.Canvas(output_file, pagesize=letter)
        self.width, self.height = letter
        self.set_up_font()
        self.id.append(self)

    def set_up_font(self):
        # تحميل الخط العربي
        pdfmetrics.registerFont(
            TTFont('Arabic', 'D:/windows_app/windows_app/static/fonts/Amiri/Amiri-Regular.ttf'))
        self.c.setFont('Arabic', 12)

    def draw_arabic_text(self, text, x, y, font_size=12):
        reshaped_text = arabic_reshaper.reshape(text)
        bidi_text = get_display(reshaped_text)
        self.c.setFont('Arabic', font_size)
        text_width = self.c.stringWidth(bidi_text, 'Arabic', font_size)
        self.c.drawString(x - text_width, y, bidi_text)

    def draw_header_image(self, header_logo):
        self.c.drawImage(header_logo, 0, self.height -
                         90, width=615, height=90)

    def draw_header(self, logo, name, address, phone_number, city):
        # إضافة الشعار في الرأس
        self.c.drawImage(logo, 40, self.height - 150, width=150, height=90)
        # معلومات الشركة في الرأس
        self.draw_arabic_text(f"{name}", self.width - 50, self.height - 40, 14)
        self.draw_arabic_text(
            f"العنوان:{address}", self.width - 50, self.height - 60, 12)
        self.draw_arabic_text(
            f"المدينة: {city}", self.width - 50, self.height - 80, 12)
        self.draw_arabic_text(
            f"الهاتف: {phone_number}", self.width - 50, self.height - 100, 12)
        self.c.line(40, 60, self.width - 40, 60)

    def draw_footer(self, account_bankname, account_fullname, account_iban):
        self.c.setFont('Arabic', 10)
        self.draw_arabic_text(
            f"اسم البنك: {account_bankname}", self.width - 50, 45, 10)
        self.draw_arabic_text(
            f"الاسم الكامل:{account_fullname} ", self.width - 50, 30, 10)
        self.draw_arabic_text(
            f"رقم الايبان :{account_iban}", self.width - 50, 15, 10)
        self.c.line(40, 60, self.width - 40, 60)

    def draw_watermark(self, water_mark):
        self.c.saveState()
        self.c.setFillColor(Color(0.6, 0.6, 0.6, alpha=0.3)
                            )  # لون رمادي فاتح وشفاف
        self.c.translate(self.width/2, self.height/2)
        self.c.rotate(45)
        # رسم الشعار
        # إعادة اللون الأصلي للعلامة المائية
        self.c.setFillColor(Color(0.6, 0.6, 0.6, alpha=0.09))
        self.c.drawImage(water_mark, -200, -200, width=400, height=400)

        self.c.restoreState()

    # رسم الرأس والذيل والعلامة المائي
    def add_data(self, order, title, client_name, costumer_address, products, product):
        # إضافة عنوان الفاتورة
        self.c.setFont('Arabic', 18)
        self.draw_arabic_text(title, self.width - 250, self.height - 150, 18)
        # معلومات العميل
        self.draw_arabic_text(
            f"اسم العميل: {client_name}", self.width - 50, self.height - 180, 14)
        self.draw_arabic_text(
            f"العنوان: {costumer_address}", self.width - 50, self.height - 200, 12)
        self.draw_arabic_text(
            f"تاريخ الفاتورة: {datetime.now().date()}", self.width - 50, self.height - 220, 12)
        self.draw_arabic_text(
            f"رقم الفاتورة: {order.id}", self.width - 200, self.height - 220, 12)
        # عنوان الجدول
        self.draw_arabic_text("الوصف", self.width - 50, self.height - 250, 12)

        self.draw_arabic_text("الكمية", self.width -
                              300, self.height - 250, 12)

        self.draw_arabic_text("السعر", self.width - 400, self.height - 250, 12)

        self.draw_arabic_text("الإجمالي", self.width -
                              500, self.height - 250, 12)

        # بيانات الفاتورة
        y = self.height - 270
        for item in products:
            self.draw_arabic_text(item.inventory.product,
                                  self.width - 50, y, 12)
            self.draw_arabic_text(str(item.quantity), self.width - 300, y, 12)
            self.draw_arabic_text(
                f"{item.inventory.price:.1f}", self.width - 400, y, 12)
            self.draw_arabic_text(
                f"{item.quantity*item.inventory.price:.1f}", self.width - 500, y, 12)
            y -= 20
        # الإجمالي الخاضع للضريبة
        self.draw_arabic_text("الإجمالي الخاضع للضريبة:",
                              self.width - 350, y - 10, 14)
        self.draw_arabic_text(
            f"{product.total_no_tax:.1f}", self.width - 500, y - 10, 14)
        # إجمالي الضريبة
        self.draw_arabic_text("إجمالي الضريبة:", self.width - 400, y - 30, 14)
        self.draw_arabic_text(f"{product.total_tax:.1f}",
                              self.width - 500, y - 30, 14)
        # المجموع الكلي
        self.draw_arabic_text("المجموع الكلي:", self.width - 400, y - 50, 14)

        self.draw_arabic_text(f"{product.total:.1f}",
                              self.width - 500, y - 50, 14)

        # حفظ الفاتورة
        self.c.save()

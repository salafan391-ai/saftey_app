import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from PIL import Image
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import arabic_reshaper
from bidi.algorithm import get_display
from utils import get_images
from database import db_session
from models import CarPartsDetection
from utils import load_data
from reportlab.lib.utils import ImageReader




class CreatePdf:
    def __init__(self, output_file):
        self.output_file = f"{output_file}.pdf"
        self.c = canvas.Canvas(self.output_file, pagesize=letter)
        self.width, self.height = letter
        self.set_up_font()
        self.db = db_session()


    def set_up_font(self):
        # Register the Arabic font
        font_path = get_images('fonts', load_data)
        pdfmetrics.registerFont(TTFont('Arabic', font_path))
        self.c.setFont('Arabic', 12)

    def draw_arabic_text(self, text, x, y, font_size=12):
        reshaped_text = arabic_reshaper.reshape(text)
        bidi_text = get_display(reshaped_text)
        self.c.setFont('Arabic', font_size)
        text_width = self.c.stringWidth(bidi_text, 'Arabic', font_size)
        self.c.drawString(x - text_width, y, bidi_text)

    def add_data(self,notes):
        y = 270
        self.draw_arabic_text('ملاحظات', 550, 290)
        notes = notes.split('  ')
        for note in notes:
            self.draw_arabic_text(note, 550, y)
            y-=20

    def header_footer(self):
        header = get_images('header', load_data)
        logo = get_images('logo', load_data)
        footer = get_images('footer', load_data)

        self.c.saveState()
        # Draw the header and footer images
        self.c.drawImage(header, 0, self.height - 90, width=615, height=90)
        self.c.drawImage(logo, 10, self.height - 70, width=100, height=40)
        self.c.drawImage(footer, 0, 0, width=615, height=90)
        self.c.restoreState()

    def draw_car_blueprint(self, img):
        self.c.drawImage(img, 70, 300, width=500, height=300)

    def save_pdf(self):
        self.c.showPage()
        self.c.save()


from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from bidi.algorithm import get_display
import arabic_reshaper
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Spacer
from reportlab.pdfgen import canvas
from datetime import datetime
from models import Contract, Customer, Order, Visits, Maintenence
from database import SessionLocal
from reportlab.lib.units import inch
import pandas as pd
from utils import get_images,load_data



def create_maintenence_pdf(id, output_file):
    pdfmetrics.registerFont(
        TTFont('Arabic', get_images('fonts',load_data)))
    session = SessionLocal()
    visits = session.query(Visits).filter_by(id=id).one()
    contract = session.query(Contract).filter_by(
        customer_id=visits.customer_id).first()

    l = []

# Iterate through each maintenance record and append the details to the list
    for i in visits.maintenences:
        l.append({
            'System Type': i.seytem_type,
            'Tool': i.tool,
            'Status': i.status,
            'Fixed': 'تم الإصلاح' if i.fixed else 'لم يتم الاصلاح بعد',
            'Cost': i.cost
        })

    # Convert the list to a pandas DataFrame
    maintenence_df = pd.DataFrame(l)

    # Function to reshape Arabic text

    def reshape_arabic_text(text):
        reshaped_text = arabic_reshaper.reshape(text)
        bidi_text = get_display(reshaped_text)
        return bidi_text

    # Custom ParagraphStyle for Arabic text
    styles = getSampleStyleSheet()

    signature_style = ParagraphStyle(
        'Arabic',
        parent=styles['Normal'],
        fontName='Arabic',  # Or any other font for English text
        fontSize=8,
        leading=20,
        textColor='darkblue',
        alignment=2,  # Left alignment for English
    )

    arabic_style = ParagraphStyle(
        'Arabic',
        parent=styles['Normal'],
        fontName='Arabic',
        textColor='darkblue',
        fontSize=6,
        leading=6,
        alignment=2,  # Right alignment for Arabic text

    )
    title_style = ParagraphStyle(
        'Arabic',
        parent=styles['Normal'],
        fontName='Arabic',
        fontSize=10,
        leading=20,
        alignment=1,
        fontWeight='bold',
        textColor='darkblue',
    )

    setup_arabic_style = ParagraphStyle(
        'Arabic',
        parent=styles['Normal'],
        fontName='Arabic',
        fontSize=8,
        leading=16,
        alignment=1,
        fontWeight='bold',
        textColor='darkblue',
    )

    var_style = ParagraphStyle(
        'Arabic',
        parent=styles['Normal'],
        textColor='darkred',
        leading=12,
        alignment=2,
        fontName='Arabic'

    )

    title_paragraph = [
        ['', Paragraph(reshape_arabic_text('محضر استلام'), title_style), '']
    ]

    company_info = [
        [Paragraph(reshape_arabic_text(f'{contract.start_date}'), var_style), Paragraph(reshape_arabic_text('Contract starting date / تاريخ بداية العقد'),
                                                                                        signature_style), Paragraph(reshape_arabic_text(f'{contract.id}'), var_style), Paragraph(reshape_arabic_text(f'Contract No. / رقم العقد'), signature_style)],
        [Paragraph(reshape_arabic_text(f'{contract.customer.name}'), var_style), Paragraph(reshape_arabic_text('Owner/Renter"s Name / اسم المالك أو المستأجر'), signature_style),
         Paragraph(reshape_arabic_text(f'{contract.customer.address}'), var_style), Paragraph(reshape_arabic_text(f'العنوان / address'), signature_style)],
        [Paragraph(reshape_arabic_text(f'{contract.customer.business_name}'), var_style), Paragraph(reshape_arabic_text(f'Facility Name / اسم المنشأة'), signature_style), Paragraph(
            reshape_arabic_text(f'{contract.customer.phone_number}'), var_style), Paragraph(reshape_arabic_text(f'Contact number/ رقم التواصل'), signature_style)],
        ['', '', Paragraph(reshape_arabic_text(f'{contract.customer.business_type}'), var_style), Paragraph(
            reshape_arabic_text('Activity Type / نوع النشاط'), signature_style)],
    ]
    engineers = [[Paragraph(reshape_arabic_text('التوقيع'), title_style), Paragraph(reshape_arabic_text(
        'المهنة'), title_style), Paragraph(reshape_arabic_text('المهندسين'), title_style)]]
    for i in visits.employees:
        engineers.append(['', Paragraph(reshape_arabic_text(
            i.career), var_style), Paragraph(reshape_arabic_text(i.fullname), var_style)])

    # Define signature fields in Arabic and reshape the text
    signature_fields = [
        ['', Paragraph(reshape_arabic_text('ختم المنشأة /العميل'), signature_style),
         '', Paragraph(reshape_arabic_text('توقيع ممثل المنشأة'), signature_style)],
        ['', Paragraph(reshape_arabic_text('الختم'), signature_style), '', Paragraph(
            reshape_arabic_text('توقيع ممثل المؤسسة'), signature_style)],

    ]
    # Print the DataFrame to verify replacements
    # Create table data
    data = [
        [
            Paragraph(reshape_arabic_text('النظام'), title_style),
            Paragraph(reshape_arabic_text('القطعة'), title_style),
            Paragraph(reshape_arabic_text('الحالة'), title_style),
            Paragraph(reshape_arabic_text('الاصلاح'), title_style),
            Paragraph(reshape_arabic_text('المبلغ'), title_style),
            Paragraph(reshape_arabic_text('المجموع'), title_style),

        ]
    ]  # Table headers
    cost = 0
    for index, row in maintenence_df.iterrows():
        cost += row['Cost']
        data.append([

            Paragraph(reshape_arabic_text(row['System Type']), var_style),
            Paragraph(reshape_arabic_text(row['Tool']), var_style),
            Paragraph(reshape_arabic_text(row['Status']), var_style),
            Paragraph(reshape_arabic_text(row['Fixed']), var_style),
            Paragraph(str(row['Cost']), setup_arabic_style),
            Paragraph(str(cost), arabic_style)

        ])

    # Define header and footer functions

    def header_footer(canvas, doc):
        canvas.saveState()
        # Draw the header images
        canvas.drawImage(get_images('header',load_data), 0,
                         doc.pagesize[1] - 90, width=615, height=90)
        canvas.drawImage(get_images('logo',load_data), 10,
                         doc.pagesize[1] - 70, width=100, height=40)
        canvas.drawImage(get_images('footer',load_data),
                         0, 0, width=615, height=90)
        canvas.restoreState()

    # Create the PDF document with header and footer
    pdf = SimpleDocTemplate(output_file, pagesize=letter,
                            topMargin=90, bottomMargin=100)

    # Create the table with the combined data
    combined_table = Table(data)
    company_info_table = Table(company_info, colWidths=[100, 180, 80, 100])
    engineers_table = Table(engineers)
    signature_fields_table = Table(signature_fields)
    title_table = Table(title_paragraph)

    # Define the table style
    style = TableStyle([
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.darkblue),
        # ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        # ('FONTNAME', (0, 0), (-1, -1), 'Arabic'),
        # ('FONTSIZE', (0, 0), (-1, -1), 8),  # Adjust font size as needed
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.darkblue),
        ('TOPPADDING', (0, 0), (-1, -1), 2),    # Reduced padding
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),  # Reduced padding
        ('LEFTPADDING', (0, 0), (-1, -1), 2),   # Reduced padding
        ('RIGHTPADDING', (0, 0), (-1, -1), 2),  # Reduced padding
    ])
    # Apply the style to the table
    combined_table.setStyle(style)
    company_info_table.setStyle(style)
    engineers_table.setStyle(style)
    signature_fields_table.setStyle(style)
    # signature_fields.setStyle(styles)
    spacer = Spacer(12, 12)
    # Build the PDF with the combined table
    pdf.build([title_table, spacer, company_info_table, spacer, combined_table, spacer,
              engineers_table, spacer, signature_fields_table], onFirstPage=header_footer)

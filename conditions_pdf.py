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
from utils import load_data, get_images
from pdf_utils import split_lines_process
from deep_translator import GoogleTranslator

rep_vars = {'أسبوع': 'one week',
            'نصف شهر': 'half a month',
            'شهر': 'one month',
            'ثلاثة أشهر': '3 months',
            'ستة أشهر': '6 months',
            'سنة': 'one year'}


def create_setup_conditions(id: int, output_file: str, condition_type: str):
    session = SessionLocal()
    contract = session.query(Contract).filter_by(id=id).first()
    # order = session.query(Order).filter_by(
    #     customer_id=contract.customer.id).first()

    # print(order.id)

    data = load_data
    df_repair = pd.read_csv('repair_conditions.csv')
    df_repair['صيانة'] = df_repair['صيانة'].apply(
        lambda x: x.replace('cost', str(contract.total_payment))).str.replace('[1]', contract.visit_cycle)
    df_repair['الترجمة'] = df_repair['الترجمة'].apply(
        lambda x: x.replace('cost', str(contract.total_payment)))
    df_repair['الترجمة'] = df_repair['الترجمة'].str.replace(
        '[1]', contract.visit_cycle).str.replace(contract.visit_cycle, rep_vars[contract.visit_cycle])
    df_repair = df_repair[['الترجمة', 'صيانة']]
    splitted_setup_data = split_lines_process(
        data.conditions[1].condition_value, 100)
    df_setup = pd.DataFrame({'تركيب': splitted_setup_data})

    # Register the Arabic font
    pdfmetrics.registerFont(
        TTFont('Arabic', get_images('fonts', data)))

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
        fontSize=14,
        leading=12,
        alignment=2,
        fontWeight='bold',
        textColor='darkblue',
    )

    setup_arabic_style = ParagraphStyle(
        'Arabic',
        parent=styles['Normal'],
        fontName='Arabic',
        fontSize=8,
        leading=10,
        alignment=2,
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

    english_style = ParagraphStyle(
        'English',
        parent=styles['Normal'],
        fontName='Helvetica',  # Or any other font for English text
        fontSize=6,
        leading=6,
        textColor='darkblue',
        alignment=0,  # Left alignment for English
    )

    title_paragraph = [
        ['', Paragraph(reshape_arabic_text(
            f"عقد {contract.description} أدوات السلامة –Safety equipment installation contract"), title_style), '']
    ]

    company_info = [
        [Paragraph(reshape_arabic_text(f'{contract.start_date.date()}'), var_style), Paragraph(reshape_arabic_text('Contract starting date / تاريخ بداية العقد'),
                                                                                               signature_style), Paragraph(reshape_arabic_text(f'{contract.id}'), var_style), Paragraph(reshape_arabic_text(f'Contract No. / رقم العقد'), signature_style)],
        [Paragraph(reshape_arabic_text(f'{contract.customer.name}'), var_style), Paragraph(reshape_arabic_text('Owner/Renter"s Name / اسم المالك أو المستأجر'), signature_style),
         Paragraph(reshape_arabic_text(f'{contract.customer.address}'), var_style), Paragraph(reshape_arabic_text(f'العنوان / address'), signature_style)],
        [Paragraph(reshape_arabic_text(f'{contract.customer.business_name}'), var_style), Paragraph(reshape_arabic_text(f'Facility Name / اسم المنشأة'), signature_style), Paragraph(
            reshape_arabic_text(f'{contract.customer.phone_number}'), var_style), Paragraph(reshape_arabic_text(f'Contact number/ رقم التواصل'), signature_style)],
        ['', '', Paragraph(reshape_arabic_text(f'{contract.customer.business_type}'), var_style), Paragraph(
            reshape_arabic_text('Activity Type / نوع النشاط'), signature_style)],
    ]

    # Define signature fields in Arabic and reshape the text
    signature_fields = [
        ['', Paragraph(reshape_arabic_text('ختم المنشأة /العميل'), signature_style),
         '', Paragraph(reshape_arabic_text('توقيع ممثل المنشأة'), signature_style)],
        ['', Paragraph(reshape_arabic_text('الختم'), signature_style), '', Paragraph(
            reshape_arabic_text('توقيع ممثل المؤسسة'), signature_style)],

    ]
    condition_variables = {
        # "[price_offer_id]": str(order.id),
        # Ensure all values are strings for replacement
        "[nums_cost]": str(contract.total_payment),
    }
    if condition_type == 'صيانة':
        df_repair['صيانة'] = df_repair['صيانة']
        list_repair_data = df_repair.to_numpy().tolist()
        # Wrap the text in the cells with the appropriate style for each column

        wrapped_data = []
        for row in list_repair_data:
            wrapped_row = []
            for index, item in enumerate(row):
                if index % 2 == 0:  # Even index represents English text
                    wrapped_row.append(Paragraph(item, english_style))
                else:  # Odd index represents Arabic text
                    wrapped_row.append(
                        Paragraph(reshape_arabic_text(item), arabic_style))
            wrapped_data.append(wrapped_row)
        # Combine all parts into one table
    # Replace keys with values in the DataFrame

    else:
        # Print the DataFrame to verify replacements
        df_setup['تركيب'] = df_setup['تركيب'].str.replace(
            '...', str(contract.completion_period)).str.replace('cost', str(contract.total_payment))
        df_setup['تركيب'] = df_setup['تركيب'].apply(reshape_arabic_text)
        list_setup_data = df_setup.to_numpy().tolist()
        wrapped_data = []
        for row in list_setup_data:
            wrapped_row = [[Paragraph(i, setup_arabic_style) for i in row]]
            wrapped_data.append(wrapped_row)

    # Define header and footer functions

    def header_footer(canvas, doc):

        header = get_images('header', data)
        logo = get_images('logo', data)
        footer = get_images('footer', data)

        canvas.saveState()
        # Draw the header images
        canvas.drawImage(header,
                         0, doc.pagesize[1] - 90, width=615, height=90)
        canvas.drawImage(logo, 10,
                         doc.pagesize[1] - 70, width=100, height=40)
        canvas.drawImage(footer,
                         0, 0, width=615, height=90)
        canvas.restoreState()

    # Create the PDF document with header and footer
    pdf = SimpleDocTemplate(output_file, pagesize=letter,
                            topMargin=90, bottomMargin=100)

    # Create the table with the combined data
    combined_table = Table(wrapped_data)
    company_info_table = Table(company_info, colWidths=[100, 180, 80, 100])
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
    # combined_table.setStyle(style)
    company_info_table.setStyle(style)
    signature_fields_table.setStyle(style)
    # signature_fields.setStyle(styles)
    spacer = Spacer(12, 12)
    # Build the PDF with the combined table
    pdf.build([title_table, spacer, company_info_table, spacer, combined_table,
              spacer, signature_fields_table], onFirstPage=header_footer)

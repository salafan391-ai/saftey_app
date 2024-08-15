from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter


def image_to_ps(image_path, ps_path):
    # Load the image using Pillow
    img = Image.open(image_path)

    # Create a PDF file using ReportLab
    c = canvas.Canvas(ps_path, pagesize=letter)
    
    # Get the dimensions of the image
    width, height = img.size

    # Draw the image onto the PDF
    c.drawImage(image_path, 0, 0, width, height)
    
    # Save the PDF file
    c.save()

# Path to the input image and the output PS file
image_path = "static/images/pngwing.com (1).png"
ps_path = "output_image.ps"

# Convert the image to PS
image_to_ps(image_path, ps_path)




import os
import subprocess
import sys
import tempfile
import time

from fpdf import FPDF

from colourpaletteextractor.model.imagedata import ImageData


def generate_report(directory: str, image_data: ImageData):
    print("Generating pdf report for image")

    # Checking if image_data is suitable

    # image_data needs to have a recoloured image and a colour palette
    if image_data.recoloured_image is None or len(image_data.colour_palette) == 0:
        print("Throw exception here")
        return

    # Create report
    pdf = _create_report(image_data)

    # Initial name and path of the report
    name = image_data.name.replace(" ", "-")
    extension = image_data.extension.replace(".", "-")
    file_name = name + extension + ".pdf"
    pdf_path = os.path.join(directory, file_name)

    # Check if PDF already exists and iterating its name if so
    count = 1
    while os.path.isfile(pdf_path):
        print(file_name + " already exists, creating new ")
        file_name = name + extension + "(" + str(count) + ")" + ".pdf"
        pdf_path = os.path.join(directory, file_name)
        count += 1

    # Writing PDF to directory
    pdf.output(pdf_path)  # This will overwrite any existing pdf with this name

    # Opening PDF by calling the system
    # new_path = r"this is my path"
    # new_path = '"pdf_path"'
    # print(new_path)

    if sys.platform == "darwin" or "linux":
        pdf_path = pdf_path.replace(" ", "\ ")  # TODO, does this work on Windows??
    else:
        pass

    pdf_path = pdf_path.replace("(", "\(")
    pdf_path = pdf_path.replace(")", "\)")


    subprocess.Popen(["open " + pdf_path], shell=True)


def _create_report(image_data: ImageData) -> FPDF:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('helvetica', 'B', 16)
    pdf.cell(40, 10, 'Hello World!')


    return pdf














    # # Create temporary PDF report
    # with tempfile.TemporaryDirectory(prefix="ColourPaletteExtractorReport_") as temp_dir_name:
    #     print('Created temporary output directory', temp_dir_name)
    #
    #     temp_pdf_path = os.path.join(temp_dir_name, "mypdf.pdf")  # PDF path
    #     pdf.output(temp_pdf_path)  # Save PDF
    #
    #     # Modifying path to be able to be opened by the system
    #     modified_path = temp_pdf_path.replace(" ", "\ ")
    #     subprocess.Popen(["open " + modified_path], shell=True)
    #
    #     time.sleep(1)  # Prevents the output directory containing the PDF from being deleted too quickly
    #     # this is a really poor way of doing this


# Create temporary directory for holding the output pdf
    # temp_dir = tempfile.TemporaryDirectory(prefix="ColourPaletteExtractorReport")
    # temp_dir_path = temp_dir.name

# temp_file = tempfile.NamedTemporaryFile(delete=False, prefix='test', suffix='.pdf')
# temporary_pdf_path = temp_file.name
# print(temporary_pdf_path)
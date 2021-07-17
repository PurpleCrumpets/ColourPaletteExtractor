import os
import subprocess
import sys
import tempfile
import time

import matplotlib.pyplot as plt
import numpy as np
from skimage.io import imsave
from fpdf import FPDF


from colourpaletteextractor.model.imagedata import ImageData


def generate_report(directory: str, image_data: ImageData):
    print("Generating pdf report for image")

    # Checking if image_data is suitable

    # image_data needs to have a recoloured image and a colour palette
    if image_data.recoloured_image is None or len(image_data.colour_palette) == 0:
        print("Throw exception here")
        return

    generator = ReportGenerator(directory=directory, image_data=image_data)

    # Create report
    pdf = generator.create_report()

    # Save report
    generator.save_report(pdf)


class ReportGenerator:

    def __init__(self, directory: str, image_data: ImageData) -> None:
        self._directory = directory
        self._image_data = image_data
        self._image_file_type = ".png"

    def save_report(self, pdf: FPDF):

        # Initial name and path of the report
        name = self._image_data.name.replace(" ", "-")
        extension = self._image_data.extension.replace(".", "-")
        file_name = name + extension + ".pdf"
        pdf_path = os.path.join(self._directory, file_name)

        # Check if PDF already exists and iterating its name if so
        count = 1
        while os.path.isfile(pdf_path):
            print(file_name + " already exists, creating new ")
            file_name = name + extension + "(" + str(count) + ")" + ".pdf"
            pdf_path = os.path.join(self._directory, file_name)
            count += 1

        # Writing PDF to directory
        pdf.output(pdf_path)  # This will overwrite any existing pdf with this name

        # Opening PDF by calling the system
        # new_path = r"this is my path"
        # new_path = '"pdf_path"'
        # print(new_path)

        # Escaping special characters
        if sys.platform == "darwin" or "linux":
            pdf_path = pdf_path.replace(" ", "\ ")  # TODO, does this work on Windows??
        else:
            pass

        pdf_path = pdf_path.replace("(", "\(")
        pdf_path = pdf_path.replace(")", "\)")

        # Opening file in default PDF viewer for system
        subprocess.Popen(["open " + pdf_path], shell=True)


        # return True  # TODO: possibly return true if all works well?

    def create_report(self) -> FPDF:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font('helvetica', 'B', 16)
        pdf.cell(40, 10, 'Hello World!')

        # Temporarily saving original and recoloured image
        self._add_image(pdf=pdf, image=self._image_data.image)  # Add original image
        self._add_image(pdf=pdf, image=self._image_data.recoloured_image)  # Add recoloured image

        # Create colour frequency chart
        self._add_chart(pdf=pdf)






        return pdf

    def _add_image(self, pdf: FPDF, image: np.array) -> None:

        # TODO: could alternatively find the original file - but it may have moved since then!

        # Create temporary file to hold the image in
        with tempfile.NamedTemporaryFile(dir=self._directory, suffix=self._image_file_type) as temp_image:

            # Save temporary image
            imsave(temp_image.name, image)

            # Add temporary image to the pdf
            pdf.image(name=temp_image.name, w=100)

    def _add_chart(self, pdf: FPDF):
        title = "Relative Frequency of Colours in Recoloured Image"

        labels = self._image_data.colour_palette
        sizes = self._image_data.colour_palette_relative_frequency

        fig, ax = plt.subplots()
        ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)

        ax.axis('equal')
        plt.tight_layout()
        plt.show()  # TODO: remove when no longer needed

        # Create temporary file to hold the image of the graph in
        with tempfile.NamedTemporaryFile(dir=self._directory, suffix=self._image_file_type) as temp_image:
            # Save temporary image

            fig.savefig(temp_image.name)

            # Add temporary image to the pdf
            pdf.image(name=temp_image.name, w=100)

        plt.close(fig)  # May not be necessary








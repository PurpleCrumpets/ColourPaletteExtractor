import os
import subprocess
import sys
import tempfile
from datetime import datetime
from typing import Union

import matplotlib
# mpl.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.container import BarContainer
import numpy as np
import seaborn as sns
from PySide2 import QtCore
from skimage.io import imsave
from fpdf import FPDF, HTMLMixin

from colourpaletteextractor import _version
from colourpaletteextractor.model.imagedata import ImageData
from colourpaletteextractor.model.model import get_settings
from colourpaletteextractor.view.tabview import NewTab

matplotlib.pyplot.switch_backend("Agg")


def generate_report(tab: NewTab, image_data: ImageData, progress_callback: QtCore.SignalInstance):

    image_data.continue_thread = True

    # Checking if image_data is suitable

    # image_data needs to have a recoloured image and a colour palette
    if image_data.recoloured_image is None or len(image_data.colour_palette) == 0:
        print("Throw exception here")
        return

    print("Generating PDF report for image...")
    generator = ReportGenerator(tab=tab, image_data=image_data,
                                progress_callback=progress_callback)

    # Create report
    pdf = generator.create_report()

    # Save report
    if pdf is not None:
        generator.save_report(pdf)
    progress_callback.emit(tab, 100)  # 100% progress


class ColourPaletteReport(FPDF, HTMLMixin):

    A4_HEIGHT = 297  # mm
    A4_WIDTH = 210  # mm
    MARGIN = 10  # mm
    IMAGE_WIDTH = 150  # mm
    IMAGE_START_POSITION = int((A4_WIDTH - IMAGE_WIDTH) / 2)  # mm
    MAX_IMAGE_HEIGHT = A4_HEIGHT - 40  # mm

    def __init__(self, image_data: ImageData):
        super().__init__()

        self._image_data = image_data

    def header(self):
        # Set font
        self.set_font('Times', 'B', 16)

        # Add title
        title_text = self._image_data.name + self._image_data.extension + " - Colour Palette Report"
        self.cell(w=0, h=0, txt=title_text, border=0, ln=2, align='C')

        self.ln(10)  # line break

    def footer(self):
        # Position 15 mm from the bottom
        self.set_y(-15)

        # Set font
        self.set_font('Times', 'I', 10)

        # Add page number
        self.cell(0, 10, 'Page ' + str(self.page_no()) + '/{nb}', 0, 0, 'C')


class ReportGenerator:

    def __init__(self, tab: NewTab, image_data: ImageData,
                 progress_callback: QtCore.SignalInstance) -> None:

        self._tab = tab
        self._image_data = image_data
        self._progress_callback = progress_callback
        self._image_file_type = ".png"
        self._continue_thread = True

        # Select output directory
        settings = get_settings()
        self._temp_dir = settings.value("output directory/temporary directory")
        if int(settings.value("output directory/use user directory")) == 0:
            self._output_dir = settings.value("output directory/temporary directory")
        elif int(settings.value("output directory/use user directory")) == 1:
            self._output_dir = settings.value("output directory/user directory")

        print("Output directory: ", self._output_dir)

        # Check if output directory exists, if not create it
        if not os.path.isdir(self._output_dir):
            print("Output directory for reports not found, creating new output directory...")
            os.makedirs(self._output_dir)
        else:
            print("Output directory for reports found...")

    def _set_progress(self, new_progress) -> None:
        self._percent = new_progress
        if self._progress_callback is not None:
            self._progress_callback.emit(self._tab, self._percent)
            self._continue_thread = self._image_data.continue_thread  # Check if thread should still be run

    def create_report(self) -> Union[ColourPaletteReport, None]:
        # Set progress bar back to zero
        self._progress_callback.emit(self._tab, 0)  # 0% progress

        pdf = ColourPaletteReport(image_data=self._image_data)
        pdf.set_margin(ColourPaletteReport.MARGIN)
        pdf.set_font('Times', 'BU', 12)
        pdf.alias_nb_pages()  # Keep track of the number of pages in the report
        pdf.set_creator(creator=_version.__application_name__)
        pdf.add_page()

        # Add original image
        print("Adding original image to report...")
        self._add_image(pdf=pdf,
                        image=self._image_data.image,
                        title="Original Image")  # Add original image
        self._set_progress(30)  # Progress = 30%
        if not self._continue_thread:
            return None

        # Add recoloured image
        print("Adding recoloured image to report...")
        self._add_image(pdf=pdf,
                        image=self._image_data.recoloured_image,
                        title="Recoloured Image")  # Add recoloured image
        self._set_progress(60)  # Progress = 60%
        if not self._continue_thread:
            return None

        # Create colour frequency chart
        print("Creating and adding colour frequency chart to report...")
        pdf.add_page()
        self._add_chart(pdf=pdf)  # Add chart
        self._set_progress(90)  # Progress = 90%
        if not self._continue_thread:
            return None

        # Add details
        self._add_details(pdf=pdf)
        self._set_progress(95)  # Progress = 95%
        if not self._continue_thread:
            return None

        return pdf

    def _add_details(self, pdf: ColourPaletteReport):
        title = "Details"
        pdf.ln(5)
        pdf.cell(w=0, h=10, txt=title, border=0, ln=1)  # Add section title

        # File name and path
        pdf.set_font('Times', '', 10)
        pdf.write(5, chr(127) + "  ")
        pdf.set_font('Times', 'U', 10)
        pdf.write(5, "Image path:\n")
        pdf.set_font('Times', '', 10)
        pdf.set_left_margin(int(ColourPaletteReport.MARGIN * 1.5))
        pdf.write(5, " - " + self._image_data.file_name_and_path)
        pdf.set_left_margin(ColourPaletteReport.MARGIN)
        pdf.ln(10)

        # Algorithm used
        algorithm = self._image_data.algorithm_used

        pdf.set_font('Times', '', 10)
        pdf.write(5, chr(127) + " ")
        pdf.set_font('Times', 'U', 10)
        pdf.write(5, "Algorithm Used:\n")

        pdf.set_font('Times', '', 10)
        pdf.set_left_margin(int(ColourPaletteReport.MARGIN * 1.5))
        pdf.write(5, " - Name: " + algorithm().name)  # Name of the algorithm
        pdf.ln(5)
        pdf.write(5, " - Class: " + str(algorithm))  # Python class
        pdf.ln(5)
        pdf.write(5, " - Reference: ")  # Python class
        # pdf.write_html('<a href="https://github.com/PyFPDF/fpdf2">Link defined as HTML</a>')
        pdf.write_html('<a href="' + algorithm().url + '">' + algorithm().url + '</a>')
        pdf.set_left_margin(ColourPaletteReport.MARGIN)
        pdf.ln(10)

        # Current data and time
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

        pdf.set_font('Times', '', 10)
        pdf.write(5, chr(127) + " ")
        pdf.set_font('Times', 'U', 10)
        pdf.write(5, "Report Generated:\n")

        pdf.set_font('Times', '', 10)
        pdf.set_left_margin(int(ColourPaletteReport.MARGIN * 1.5))
        pdf.write(5, " - " + dt_string)
        pdf.set_left_margin(ColourPaletteReport.MARGIN)
        pdf.ln(10)

    def save_report(self, pdf: ColourPaletteReport):

        # Initial name and path of the report
        name = self._image_data.name.replace(" ", "-")
        extension = self._image_data.extension.replace(".", "-")
        file_name = name + extension + ".pdf"
        pdf_path = os.path.join(self._output_dir, file_name)

        # Check if PDF already exists and iterating its name if so
        count = 1
        while os.path.isfile(pdf_path):
            print(file_name + " already exists, trying to find a valid name...")
            file_name = name + extension + '(' + str(count) + ')' + '.pdf'
            pdf_path = os.path.join(self._output_dir, file_name)
            count += 1

        # Writing PDF to directory
        pdf.output(pdf_path)  # This will overwrite any existing pdf with this name

        # Escaping special characters for system call
        if sys.platform == "darwin" or sys.platform == "linux":
            pdf_path = pdf_path.replace(" ", "\ ")
            pdf_path = pdf_path.replace("(", "\(")
            pdf_path = pdf_path.replace(")", "\)")

        else:
            # This is weirdly only necessary if the path has no spaces
            if " " not in pdf_path:
                pdf_path = pdf_path.replace("(", "^(")
                pdf_path = pdf_path.replace(")", "^)")

        # Opening file in default PDF viewer for system
        print(pdf_path)

        # Opening PDF by calling the system
        print("Opening PDF report...")
        if sys.platform == "win32":
            subprocess.Popen(pdf_path, shell=True)
        else:
            subprocess.Popen(["open " + pdf_path], shell=True)

        # return True  # TODO: possibly return true if all works well?

    def _add_image(self, pdf: ColourPaletteReport, image: np.array, title: str) -> None:

        # Create temporary file to hold the image in
        temp_image = tempfile.NamedTemporaryFile(dir=self._temp_dir,
                                                 suffix=self._image_file_type,
                                                 mode='w',
                                                 delete=False)

        print(pdf.get_y())
        # Save temporary image and close file
        imsave(temp_image.name, image)
        temp_image.close()

        # Image dimensions
        height = image.shape[0]
        width = image.shape[1]

        # Select appropriate image dimensions for report
        new_height = ColourPaletteReport.IMAGE_WIDTH / width * height

        if new_height > ColourPaletteReport.MAX_IMAGE_HEIGHT:  # Image will be too tall when scaled to the default width
            new_width = int(ColourPaletteReport.MAX_IMAGE_HEIGHT / height * width)
            new_start_position = int((ColourPaletteReport.A4_WIDTH - new_width) / 2)  # mm

        elif width < ColourPaletteReport.IMAGE_WIDTH:  # Image will be scaled up and look terrible
            new_width = int(width * 2 / 3)
            new_start_position = int((ColourPaletteReport.A4_WIDTH - new_width) / 2)  # mm

        elif (pdf.get_y() + new_height + 10) > ColourPaletteReport.MAX_IMAGE_HEIGHT:  # Image and caption won't fit on current page
            pdf.add_page()
            new_width = ColourPaletteReport.IMAGE_WIDTH  # Default width
            new_start_position = ColourPaletteReport.IMAGE_START_POSITION  # Default image position
        else:
            new_width = ColourPaletteReport.IMAGE_WIDTH  # Default width
            new_start_position = ColourPaletteReport.IMAGE_START_POSITION  # Default image position

        # Add temporary image to the pdf
        pdf.image(name=temp_image.name, w=new_width, x=new_start_position)

        pdf.cell(w=0, h=5, txt=title, border=0, ln=1, align="C")  # Add image title
        pdf.ln(h=5)  # Space after image

        # Removing temporary image file
        os.remove(temp_image.name)

    def _add_chart(self, pdf: ColourPaletteReport):

        # Create bar plot
        figure, ax = self._create_bar_plot()

        # Create temporary file to hold the image of the graph in
        temp_image = tempfile.NamedTemporaryFile(dir=self._temp_dir,
                                                 suffix=self._image_file_type,
                                                 mode='w',
                                                 delete=False)

        # Save temporary image and close file
        figure.savefig(temp_image.name, bbox_inches='tight')
        figure.clf()
        # plt.close(figure)
        temp_image.close()

        # Add temporary image to the pdf
        title = "Relative Frequency of Colours in Recoloured Image"
        # pdf.cell(w=20, h=10, ln=0)  # Add indent
        pdf.cell(w=0, h=10, txt=title, border=0, ln=1, align="C")  # Add chart title
        pdf.image(name=temp_image.name,
                  w=ColourPaletteReport.IMAGE_WIDTH,
                  x=ColourPaletteReport.IMAGE_START_POSITION)

        # Delete temporary image file
        os.remove(temp_image.name)

    def _create_bar_plot(self):

        # Get data and labels
        raw_labels = self._image_data.colour_palette
        data = self._image_data.colour_palette_relative_frequency

        # Format labels
        labels = []
        for label in raw_labels:
            label = "[" + str(label[0]) + ", " + str(label[1]) + ", " + str(label[2]) + "]"
            labels.append(label)

        # Rescale relative frequencies from 0-1, to 0-100
        data = np.array(data)
        data = data * 100

        # Create plot
        sns.set_theme(style="ticks", context="paper")
        fig, ax = plt.subplots()
        ax = sns.barplot(x=labels, y=data, edgecolor="black")

        # Set title and axis labels
        # ax.set_title(label="Relative Frequency of Colours in Recoloured Image", fontsize=16)
        ax.set_xlabel(xlabel="Colour Palette", fontsize=11)
        ax.set_ylabel(ylabel="Relative Frequency (%)", fontsize=11)

        # Format tick labels
        # for tick in ax.xaxis.get_major_ticks():  # X-axis tick labels
        #     tick.label.set_fontsize(6)

        # for tick in ax.yaxis.get_major_ticks():  # Y-axis tick labels
        #     tick.label.set_fontsize(8)

        ax.set_xticklabels(ax.get_xticklabels(), rotation=45, horizontalalignment='right')  # Rotate tick labels

        # Rescale RGB colour values to between 0 and 1
        colours = np.asarray(raw_labels, dtype=np.float32)
        colours = colours / 255

        # Recolour bars in graph to correspond to the colours in the palette
        bars = [i for i in ax.containers if isinstance(i, BarContainer)]
        if len(bars) == 1:
            for i in range(0, len(raw_labels)):
                bar = bars[0][i]
                bar.set_color(colours[i][:])
                bar.set_edgecolor("black")
        else:
            # TODO: throw exception here! if more than one bar container
            print("More than one bar container found! ", len(raw_labels))
            pass

        return fig, ax







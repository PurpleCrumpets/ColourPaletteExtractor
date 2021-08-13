# ColourPaletteExtractor is a simple tool to generate the colour palette of an image.
# Copyright (C) 2021  Tim Churchfield
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


import os
import subprocess
import sys
import tempfile
from datetime import datetime
from typing import Union

import matplotlib
import matplotlib.pyplot as plt
from PySide2.QtCore import QSettings
from matplotlib.container import BarContainer
from matplotlib.figure import Figure
from matplotlib.axes import SubplotBase
import numpy as np
import seaborn as sns
from PySide2 import QtCore

from skimage.io import imsave
from fpdf import FPDF, HTMLMixin

from colourpaletteextractor import _version
from colourpaletteextractor import _settings
from colourpaletteextractor.model.imagedata import ImageData
from colourpaletteextractor.view.tabview import NewTab

matplotlib.pyplot.switch_backend("Agg")  # Allow for plotting of non-interactive plots


def generate_report(tab: NewTab, image_data: ImageData, settings: QSettings,
                    progress_callback: QtCore.SignalInstance) -> None:
    """Generate a colour palette report for an image.

    Args:
        tab (NewTab): The tab associated with the image to be analysed.
        image_data (ImageData): The ImageData object holding the image's data (the original image, the recoloured image,
            and the colour palette).
        settings (QSettings): The settings for the ColourPaletteExtraction application.
        progress_callback (QtCore.SignalInstance): Signal that when emitted, is used to update the GUI.

    Raises:
        ValueError: If the provided ImageData object does not have a recoloured image or has no colours in its colour
            palette.

    """

    image_data.continue_thread = True  # Set thread status to run (True)

    # Check if image_data is suitable (image_data needs to have a recoloured image and a colour palette)
    if image_data.recoloured_image is None:
        raise ValueError("The provided ImageData object does not have a recoloured image!")

    if len(image_data.colour_palette) == 0:
        raise ValueError("The provided ImageData object does not have any colours in the colour palette!")

    # Get report generator object
    generator = ReportGenerator(tab=tab, image_data=image_data, settings=settings,
                                progress_callback=progress_callback)

    # Create report
    pdf = generator.create_report()

    # Save report
    if pdf is not None:
        generator.save_report(pdf)
    progress_callback.emit(tab, 100)  # 100% progress


class ColourPaletteReport(FPDF, HTMLMixin):
    """A modified FPDF object to fit the requirements for generating a PDF colour palette report.

    Args:
        image_data (ImageData): The ImageData object holding the image's data (the original image, the recoloured image,
            and the colour palette).
    """

    A4_HEIGHT = 297  # mm
    """The height of an A4 sheet of paper (mm)."""

    A4_WIDTH = 210  # mm
    "The width of an A4 sheet of paper (mm)."

    MARGIN = 10  # mm
    "The size of the margins to be used in the PDF report (mm)."

    IMAGE_WIDTH = 150  # mm
    "The standard width of images in the PDF report (mm)."

    IMAGE_START_POSITION = int((A4_WIDTH - IMAGE_WIDTH) / 2)  # mm
    """The standard left indentation when placing an image in the PDF report (mm)."""

    MAX_IMAGE_HEIGHT = A4_HEIGHT - 40  # mm
    "The standard maximum height of images in the report (mm)."

    def __init__(self, image_data: ImageData):
        super().__init__()

        self._image_data = image_data

    def header(self) -> None:
        """Set the header used in the PDF report."""

        # Set font
        self.set_font('Times', 'B', 16)

        # Add title
        title_text = self._image_data.name + self._image_data.extension + " - Colour Palette Report"
        self.cell(w=0, h=0, txt=title_text, border=0, ln=2, align='C')

        self.ln(10)  # line break

    def footer(self) -> None:
        """Set the footer used in the PDF report."""

        # Position 15 mm from the bottom
        self.set_y(-15)

        # Set font
        self.set_font('Times', 'I', 10)

        # Add page number
        self.cell(0, 10, 'Page ' + str(self.page_no()) + '/{nb}', 0, 0, 'C')


class ReportGenerator:
    """Class used to create, populate a :class:`ColourPaletteReport` object and save the resulting PDF to disk.

    Args:
        tab (NewTab): The tab associated with the image to be analysed.
        image_data (ImageData): The ImageData object holding the image's data (the original image, the recoloured image,
            and the colour palette).
        settings (QSettings): The settings for the ColourPaletteExtraction application.
        progress_callback (QtCore.SignalInstance): Signal that when emitted, is used to update the GUI.
    """

    def __init__(self, tab: NewTab, image_data: ImageData, settings: QSettings,
                 progress_callback: QtCore.SignalInstance) -> None:

        self._tab = tab
        self._image_data = image_data
        self._progress_callback = progress_callback
        self._image_file_type = ".png"  # Images created as part of the report are saved as a PNG file
        self._continue_thread = True  # Execution status of the thread

        # Select output directory
        self._temp_dir = settings.value("output directory/temporary directory")
        if int(settings.value("output directory/use user directory")) == 0:
            self._output_dir = settings.value("output directory/temporary directory")
        elif int(settings.value("output directory/use user directory")) == 1:
            self._output_dir = settings.value("output directory/user directory")

        # Check if output directory exists, if not create it
        if not os.path.isdir(self._output_dir):
            if _settings.__VERBOSE__:
                print("Output directory for colour palette reports not found, creating new output directory...")
            os.makedirs(self._output_dir)
        else:
            if _settings.__VERBOSE__:
                print("Output directory for colour palette reports found...")

        if _settings.__VERBOSE__:
            print("Output directory for colour palette report: ", self._output_dir)

    def _set_progress(self, new_progress) -> None:
        """Set the algorithm progress to a new value and possibly notify the GUI of the change.

        Args:
            new_progress (float): New value of the progress bar.

        Raises:
            ValueError: If the new progress value is greater than 100%.

        """

        if new_progress > 100:
            raise ValueError("Algorithm's progress cannot be larger than 100%.")

        self._percent = new_progress
        if self._progress_callback is not None:
            self._progress_callback.emit(self._tab, self._percent)
            self._continue_thread = self._image_data.continue_thread  # Check if the thread should still be run

    def create_report(self) -> Union[ColourPaletteReport, None]:
        """Create a :class:`ColourPaletteReport` object representing the PDF colour palette report.

        Returns:
            (Union[ColourPaletteReport, None]): None if the :class:`ColourPaletteReport` object was not properly
                generated, otherwise returns the populated :class:`ColourPaletteReport` object.

        """

        # Set progress bar back to zero
        self._progress_callback.emit(self._tab, 0)  # 0% progress

        pdf = ColourPaletteReport(image_data=self._image_data)
        pdf.set_margin(ColourPaletteReport.MARGIN)
        pdf.set_font('Times', 'BU', 12)
        pdf.alias_nb_pages()  # Keep track of the number of pages in the report
        pdf.set_creator(creator=_version.__application_name__)
        pdf.add_page()

        # Add original image
        if _settings.__VERBOSE__:
            print("Adding original image to report...")
        self._add_image(pdf=pdf,
                        image=self._image_data.image,
                        title="Original Image")  # Add original image
        self._set_progress(30)  # Progress = 30%
        if not self._continue_thread:
            return None

        # Add recoloured image
        if _settings.__VERBOSE__:
            print("Adding recoloured image to report...")
        self._add_image(pdf=pdf,
                        image=self._image_data.recoloured_image,
                        title="Recoloured Image")  # Add recoloured image
        self._set_progress(60)  # Progress = 60%
        if not self._continue_thread:
            return None

        # Create colour frequency chart
        if _settings.__VERBOSE__:
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

    def save_report(self, pdf: ColourPaletteReport) -> None:
        """save the :class:`ColourPaletteReport` object representing the PDF colour palette report to disk.

        Args:
            pdf (ColourPaletteReport): The :class:`ColourPaletteReport` object to be saved as a PDF to disk..

        """

        # Initial name and path of the report
        name = self._image_data.name.replace(" ", "-")
        extension = self._image_data.extension.replace(".", "-")
        file_name = name + extension + ".pdf"
        pdf_path = os.path.join(self._output_dir, file_name)

        # Check if PDF already exists and iterating its name if so
        count = 1
        while os.path.isfile(pdf_path):
            if _settings.__VERBOSE__:
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

        # Opening PDF by calling the system
        if _settings.__VERBOSE__:
            print("Opening colour palette PDF report...")
        if sys.platform == "win32":
            subprocess.Popen(pdf_path, shell=True)
        else:
            subprocess.Popen(["open " + pdf_path], shell=True)

    def _add_details(self, pdf: ColourPaletteReport) -> None:
        """Add the details section to the PDF.

        Args:
            pdf (ColourPaletteReport): The :class:`ColourPaletteReport` object to have the details section added to.

        """

        title = "Details"
        pdf.ln(5)
        pdf.cell(w=0, h=10, txt=title, border=0, ln=1)  # Add section title

        # Description of what recoloured image means
        pdf.set_font('Times', '', 10)
        pdf.write(5, "The recoloured image is created by reassigning each pixel's colour to the most representative "
                  + "colour found in the colour palette. For the algorithm proposed by Nieves et al. (2020), this "
                  + "is the colour in the colour palette that is closest to the pixel's colour in the CIELAB colour"
                  + " space (the shortest Euclidean distance). The graph above shows the relative frequency of the"
                  + " colours in the colour palette when used to recolour the original image. On the X-axis, each label"
                  + " refers to the colour's sRGB triplet.")
        pdf.ln(10)

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

    def _add_image(self, pdf: ColourPaletteReport, image: np.array, title: str) -> None:
        """

        Args:
            pdf (ColourPaletteReport): The :class:`ColourPaletteReport` object to have the image added to.
            image (np.array): Array representation of the image to be added to the PDF report.
            title (str): The title of the image to be added to the report.

        """

        # Create temporary file to hold the image in
        temp_image = tempfile.NamedTemporaryFile(dir=self._temp_dir,
                                                 suffix=self._image_file_type,
                                                 mode='w',
                                                 delete=False)

        # Save temporary image and close file
        imsave(temp_image.name, image)
        temp_image.close()

        # Image dimensions
        height = image.shape[0]
        width = image.shape[1]

        # Select appropriate image dimensions and position within the report
        new_height = ColourPaletteReport.IMAGE_WIDTH / width * height

        if new_height > ColourPaletteReport.MAX_IMAGE_HEIGHT:  # Image will be too tall when scaled to the default width
            new_width = int(ColourPaletteReport.MAX_IMAGE_HEIGHT / height * width)
            new_start_position = int((ColourPaletteReport.A4_WIDTH - new_width) / 2)  # (mm)

        elif width < ColourPaletteReport.IMAGE_WIDTH:  # Image will be scaled up and look terrible
            new_width = int(width * 2 / 3)
            new_start_position = int((ColourPaletteReport.A4_WIDTH - new_width) / 2)  # (mm)

        elif (pdf.get_y() + new_height + 10) > ColourPaletteReport.MAX_IMAGE_HEIGHT:  # Image, caption don't fit on page
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

    def _add_chart(self, pdf: ColourPaletteReport) -> None:
        """Add a bar chart portraying the relative frequencies of the colours in the recoloured image to the report.

        Args:
            pdf (ColourPaletteReport): The :class:`ColourPaletteReport` object to have the bar chart added to.

        """

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
        temp_image.close()

        # Add temporary image to the pdf
        title = "Relative Frequency of Colours in Recoloured Image"
        pdf.cell(w=0, h=10, txt=title, border=0, ln=1, align="C")  # Add chart title
        pdf.image(name=temp_image.name,
                  w=ColourPaletteReport.IMAGE_WIDTH,
                  x=ColourPaletteReport.IMAGE_START_POSITION)

        # Delete temporary image file
        os.remove(temp_image.name)

    def _create_bar_plot(self) -> tuple[Figure, SubplotBase]:
        """Create and returns the relative frequency colour palette bar chart.

        Returns:
            (Figure): The figure holding the bar plot.
            (SubplotBase):  THe axes of the bar plot (technically a matplotlib.axes._subplots.AxesSubplot object).

        """

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
            ValueError("The number of bar containers does not equal one for the given plot ("
                       + str(len(bars)) + ") found.")

        return fig, ax

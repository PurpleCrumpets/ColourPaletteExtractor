import os
import stat
import subprocess
import sys
import tempfile
import time
import warnings

import matplotlib
# mpl.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.container import BarContainer
import numpy as np
import seaborn as sns
from PySide2 import QtCore
from skimage.io import imsave
from fpdf import FPDF

from colourpaletteextractor.model.imagedata import ImageData
from colourpaletteextractor.view.tabview import NewTab

matplotlib.pyplot.switch_backend("Agg")


def generate_report(directory: str, tab: NewTab, image_data: ImageData, progress_callback: QtCore.SignalInstance):
    # old_dir = directory
    # print(old_dir)
    # directory = "C:\\Users\\timch\\OneDrive - University of St Andrews\\University\\MScProject\\Test Dir"
    # print(directory)

    # Checking if image_data is suitable

    # image_data needs to have a recoloured image and a colour palette
    if image_data.recoloured_image is None or len(image_data.colour_palette) == 0:
        print("Throw exception here")
        return

    print("Generating PDF report for image...")
    generator = ReportGenerator(directory=directory, tab=tab, image_data=image_data,
                                progress_callback=progress_callback)

    # Create report
    pdf = generator.create_report()

    # Save report
    generator.save_report(pdf)
    progress_callback.emit(tab, 100)  # 100% progress


class ReportGenerator:

    def __init__(self, directory: str, tab: NewTab, image_data: ImageData,
                 progress_callback: QtCore.SignalInstance) -> None:
        self._directory = directory
        self._tab = tab
        self._image_data = image_data
        self._progress_callback = progress_callback
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
            print(file_name + " already exists, trying to find a valid name...")
            file_name = name + extension + '(' + str(count) + ')' + '.pdf'
            pdf_path = os.path.join(self._directory, file_name)
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

    def create_report(self) -> FPDF:
        # Set progress bar back to zero
        self._progress_callback.emit(self._tab, 0)  # 0% progress

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font('helvetica', 'B', 16)
        pdf.cell(40, 10, 'Hello World!')

        # Temporarily saving original and recoloured image
        print("Adding original image to report...")
        self._add_image(pdf=pdf, image=self._image_data.image)  # Add original image
        self._progress_callback.emit(self._tab, 30)  # 30% progress

        print("Adding recoloured image to report...")
        self._add_image(pdf=pdf, image=self._image_data.recoloured_image)  # Add recoloured image
        self._progress_callback.emit(self._tab, 60)  # 60% progress

        # Create colour frequency chart
        print("Creating and adding colour frequency chart to report...")
        self._add_chart(pdf=pdf)
        self._progress_callback.emit(self._tab, 90)  # 90% progress

        return pdf

    def _add_image(self, pdf: FPDF, image: np.array) -> None:

        # TODO: could alternatively find the original file - but it may have moved since then!

        # Create temporary file to hold the image in
        temp_image = tempfile.NamedTemporaryFile(dir=self._directory,
                                                 suffix=self._image_file_type,
                                                 mode='w',
                                                 delete=False)

        # Change file permissions
        # os.chmod(temp_image.name, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)

        # Save temporary image and close file
        imsave(temp_image.name, image)
        temp_image.close()

        # Add temporary image to the pdf
        pdf.image(name=temp_image.name, w=100)

        # Removing temporary image file
        os.remove(temp_image.name)

    def _add_chart(self, pdf: FPDF):
        # plt.ioff()  # Disable interactive plotting

        plot = self._create_bar_plot()
        fig = plot.get_figure()

        # Create temporary file to hold the image of the graph in
        temp_image = tempfile.NamedTemporaryFile(dir=self._directory,
                                                 suffix=self._image_file_type,
                                                 mode='w',
                                                 delete=False)

        # Change file permissions
        # os.chmod(temp_image.name, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)

        # Save temporary image and close file
        fig.savefig(temp_image.name, bbox_inches='tight')
        temp_image.close()

        # Add temporary image to the pdf
        pdf.image(name=temp_image.name, w=150)

        # Delete temporary image file
        os.remove(temp_image.name)

        plt.close(fig)  # May not be necessary

    def _create_bar_plot(self):

        # Get data and labels
        raw_labels = self._image_data.colour_palette
        data = self._image_data.colour_palette_relative_frequency

        # Format labels
        labels = []
        for label in raw_labels:
            label = "[" + str(label[0]) + ", " + str(label[1]) + ", " + str(label[2]) + "]"
            labels.append(label)

        # Create plot
        sns.set_theme(style="ticks", context="paper")
        ax = sns.barplot(x=labels, y=data)

        # Set title and axis labels
        ax.set_title(label="Relative Frequency of Colours in Recoloured Image", fontsize=16)
        ax.set_xlabel(xlabel="Colour Palette", fontsize=10)
        ax.set_ylabel(ylabel="Relative Frequency", fontsize=10)

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
                bars[0][i].set_color(colours[i][:])
        else:
            # TODO: throw exception here!
            pass

        return ax

from colourpaletteextractor.model.algorithms.nieves2020 import Nieves2020
from colourpaletteextractor.model.model import generate_colour_palette_from_image

# Path to sample image
file_name = "./colourpaletteextractor//data/sampleImages/annunciation-1434.jpg"

# Using the default algorithm
print("Using the default algorithm")
recoloured_image, colour_palette, relative_frequencies = generate_colour_palette_from_image(file_name)

# Specifying the algorithm to use
print("Specifying the algorithm to use")
recoloured_image, colour_palette, relative_frequencies = generate_colour_palette_from_image(path_to_file=file_name,
                                                                                            algorithm=Nieves2020)
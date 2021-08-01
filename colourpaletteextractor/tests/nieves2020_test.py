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


from colourpaletteextractor.model.algorithms import nieves2020
from colourpaletteextractor.tests.helpers import helperfunctions


def test_nieves2020_offset_cubes_constructor():

    algorithm = nieves2020.Nieves2020OffsetCubes()

    assert algorithm.name == "Nieves, Gomez-Robledo, Chen and Romero (2020) - Cube corners at CIELAB origin"
    assert algorithm.url == "https://doi.org/10.1364/AO.378659"

    # Check default parameters
    assert algorithm._progress_callback is None
    assert algorithm._tab is None
    assert algorithm._image_data is None
    assert algorithm._percent == 0

    # Execution status of algorithm
    assert algorithm.continue_thread is True


def test_nieves2020_centred_cubes_constructor():
    algorithm = nieves2020.Nieves2020CentredCubes()

    assert algorithm.name == "Nieves, Gomez-Robledo, Chen and Romero (2020) - Cube centred on CIELAB origin"
    assert algorithm.url == "https://doi.org/10.1364/AO.378659"

    # Check default parameters
    assert algorithm._progress_callback is None
    assert algorithm._tab is None
    assert algorithm._image_data is None
    assert algorithm._percent == 0

    # Execution status of algorithm
    assert algorithm.continue_thread is True


def test_recoloured_image_of_same_size_1():
    image = helperfunctions.get_image("./colourpaletteextractor/tests/testImages/all-black-60x60.png")
    # black image sRGB[0, 0, 0]

    algorithm = nieves2020.Nieves2020CentredCubes()
    recoloured_image, colour_palette, relative_frequencies = algorithm.generate_colour_palette(image)

    assert image.shape[0] == recoloured_image.shape[0]
    assert image.shape[1] == recoloured_image.shape[1]


def test_recoloured_image_two_colours_1():
    image = helperfunctions.get_image("./colourpaletteextractor/tests/testImages/half-black-grey-60x60.png")
    # half black sRGB[0, 0, 0]
    # half grey sRGB[38, 38, 38]
    # Should return two colours in the colour palette with no merging of colours

    algorithm = nieves2020.Nieves2020CentredCubes()
    recoloured_image, colour_palette, relative_frequencies = algorithm.generate_colour_palette(image)

    # Convert colour_palette to list
    colour_palette = [list(colour) for colour in colour_palette]
    assert len(colour_palette) == 2
    assert [0, 0, 0] in colour_palette
    assert [38, 38, 38] in colour_palette

    assert len(relative_frequencies) == 2
    assert relative_frequencies[0] == relative_frequencies[1]
    assert relative_frequencies[0] == 0.5


def test_recoloured_image_two_colours_2():
    image = helperfunctions.get_image("./colourpaletteextractor/tests/testImages/half-black-dark-grey-60x60.png")
    # half black sRGB[0, 0, 0]
    # half grey sRGB[24, 24, 24]
    # Should return one colour in the colour palette

    algorithm = nieves2020.Nieves2020CentredCubes()
    recoloured_image, colour_palette, relative_frequencies = algorithm.generate_colour_palette(image)

    # Convert colour_palette to list
    colour_palette = [list(colour) for colour in colour_palette]
    assert len(colour_palette) == 1
    assert [14, 14, 14] in colour_palette
    assert [0, 0, 0] not in colour_palette
    assert [38, 38, 38] not in colour_palette

    assert len(relative_frequencies) == 1
    assert relative_frequencies[0] == 1


def test_cube_colour_must_occur_more_than_three_percent_threshold_to_be_included_1():
    image = helperfunctions.get_image("./colourpaletteextractor/tests/testImages/399-black-1-pink.png")
    # Colour 1: 0.25% sRGB[246, 144, 111] -> LAB[70, 35, 34]
    # Colour 2: 99.75% sRGB[0, 0, 0]
    # Colour 1 does not occur enough to be relevant
    # DOESN'T MEET SECONDARY RELEVANCY REQUIREMENTS

    algorithm = nieves2020.Nieves2020CentredCubes()
    recoloured_image, colour_palette, relative_frequencies = algorithm.generate_colour_palette(image)

    # Convert colour_palette to list
    colour_palette = [list(colour) for colour in colour_palette]

    assert len(colour_palette) == 1


def test_cube_colour_must_occur_more_than_three_percent_threshold_to_be_included_2():
    image = helperfunctions.get_image("./colourpaletteextractor/tests/testImages/99-black-1-pink.png")
    # Colour 1: 1% sRGB[246, 144, 111] -> LAB[70, 35, 34]
    # Colour 2: 99% sRGB[0, 0, 0]
    # Colour 1 meets secondary C* relevancy requirements

    algorithm = nieves2020.Nieves2020CentredCubes()
    recoloured_image, colour_palette, relative_frequencies = algorithm.generate_colour_palette(image)

    # Convert colour_palette to list
    colour_palette = [list(colour) for colour in colour_palette]

    assert len(colour_palette) == 2

    assert [246, 145, 111] in colour_palette  # Possible rounding error here
    assert [0, 0, 0] in colour_palette


def test_two_colours_in_same_cube_can_meet_secondary_threshold_1():
    image = helperfunctions.get_image("./colourpaletteextractor/tests/testImages/98-black-1-pink-1-another-pink.png")
    # Colour 1: 1% sRGB[246, 144, 111] -> LAB[70, 35, 34]
    # Colour 2: 1% sRGB[246 144 109] -> LAB[70, 35, 35]
    # Colour 3: 98% sRGB[0, 0, 0]
    # Colour 1 and 2 should be in the same cube but not enough to be considered relevant by primary
    # requirement, but meet secondary relevancy requirements for C*

    algorithm = nieves2020.Nieves2020CentredCubes()
    recoloured_image, colour_palette, relative_frequencies = algorithm.generate_colour_palette(image)

    # Convert colour_palette to list
    colour_palette = [list(colour) for colour in colour_palette]

    assert len(colour_palette) == 2

    assert [0, 0, 0] in colour_palette
    assert [246, 143, 110] in colour_palette  # Possible rounding issues

    assert 0.98 == relative_frequencies[colour_palette.index([0, 0, 0])]
    assert 0.02 == relative_frequencies[colour_palette.index([246, 143, 110])]


def test_low_a_b_colour_does_not_meet_secondary_requirements_1():
    image = helperfunctions.get_image("./colourpaletteextractor/tests/testImages/1-grey-99-white.png")

    # Colour 1: 1% sRGB[196, 196, 196] -> LAB[79, 0, 0]
    # Colour 2: 99% sRGB[255, 255, 255] -> LAB[100, 0, 0]
    # Colour 1 has too low L* to meet secondary requirements
    # Colour 1 has too low C* to meet secondary requirements

    algorithm = nieves2020.Nieves2020CentredCubes()
    recoloured_image, colour_palette, relative_frequencies = algorithm.generate_colour_palette(image)

    # Convert colour_palette to list
    colour_palette = [list(colour) for colour in colour_palette]

    assert len(colour_palette) == 1
    assert [255, 255, 255] in colour_palette


def test_low_a_b_colour_does_not_meet_secondary_requirements_2():
    image = helperfunctions.get_image("./colourpaletteextractor/tests/testImages/2-grey-98-white.png")

    # Colour 1: 2% sRGB[196, 196, 196] -> LAB[79, 0, 0]
    # Colour 2: 98% sRGB[255, 255, 255] -> LAB[100, 0, 0]
    # Colour 1 has too low L* to meet secondary requirements
    # Colour 1 has too low C* to meet secondary requirements

    algorithm = nieves2020.Nieves2020CentredCubes()
    recoloured_image, colour_palette, relative_frequencies = algorithm.generate_colour_palette(image)

    # Convert colour_palette to list
    colour_palette = [list(colour) for colour in colour_palette]

    assert len(colour_palette) == 1
    assert [255, 255, 255] in colour_palette


def test_primary_requirements_1():
    image = helperfunctions.get_image("./colourpaletteextractor/tests/testImages/3-grey-97-white.png")

    # Colour 1: 3% sRGB[196, 196, 196] -> LAB[79, 0, 0]
    # Colour 2: 97% sRGB[255, 255, 255] -> LAB[100, 0, 0]
    # Colour 1 doesn't meet the three percent (equal to not greater than!) as stated in paper

    algorithm = nieves2020.Nieves2020CentredCubes()
    recoloured_image, colour_palette, relative_frequencies = algorithm.generate_colour_palette(image)

    # Convert colour_palette to list
    colour_palette = [list(colour) for colour in colour_palette]

    assert len(colour_palette) == 1
    assert [255, 255, 255] in colour_palette

    assert 1 == relative_frequencies[colour_palette.index([255, 255, 255])]


def test_primary_requirements_2():
    image = helperfunctions.get_image("./colourpaletteextractor/tests/testImages/4-grey-96-white.png")

    # Colour 1: 4% sRGB[196, 196, 196] -> LAB[79, 0, 0]
    # Colour 2: 96% sRGB[255, 255, 255] -> LAB[100, 0, 0]
    # Colour 1 meets the primary requirements threshold

    algorithm = nieves2020.Nieves2020CentredCubes()
    recoloured_image, colour_palette, relative_frequencies = algorithm.generate_colour_palette(image)

    # Convert colour_palette to list
    colour_palette = [list(colour) for colour in colour_palette]

    assert len(colour_palette) == 2
    assert [255, 255, 255] in colour_palette
    assert [196, 196, 196] in colour_palette


def test_primary_requirements_3():
    image = helperfunctions.get_image("./colourpaletteextractor/tests/testImages/multi-colour-1.png")

    # Colour 1:  4% sRGB[0, 0, 0]       -> LAB[0, 0, 0] - good
    # Colour 2:  4% sRGB[48, 48, 48]    -> LAB[20, 0, 0] - good
    # Colour 3:  4% sRGB[94, 94, 94]    -> LAB[40, 0, 0] - good
    # Colour 4:  4% sRGB[145, 145, 145] -> LAB[60, 0, 0] - good
    # Colour 5:  4% sRGB[198, 198, 198] -> LAB[80, 0, 0] - good
    # Colour 6:  4% sRGB[255, 255, 255] -> LAB[80, 20, 20] - good

    # Colour 7:  4% sRGB[244, 184, 162] -> LAB[80, 20, 20] - good
    # Colour 8:  4% sRGB[180, 208, 121] -> LAB[80, -20, 40] - good
    # Colour 9:  4% sRGB[135, 218, 119] -> LAB[80, -40, 40] - good
    # Colour 10: 4% sRGB[0, 238, 255]   -> LAB[80, -80, -100] - good
    # Colour 11: 4% sRGB[255, 155, 255] -> LAB[80, 60, -60] - good
    # Colour 12: 4% sRGB[136, 154, 0]   -> LAB[60, -20, 100] - good

    # Colour 13: 4% sRGB[103, 155, 144] -> LAB[60, -20, 0] - good
    # Colour 14: 4% sRGB[255, 72, 0]    -> LAB[80, 100, 100] - good
    # Colour 15: 4% sRGB[19, 163, 144]  -> LAB[60, -40, 0] - good
    # Colour 16: 4% sRGB[0, 69, 0]      -> LAB[20, -100, 60] - good
    # Colour 17: 4% sRGB[0, 71, 107]    -> LAB[20, -100, -40] - good
    # Colour 18: 4% sRGB[0, 79, 205]    -> LAB[20, -100, -100] - good

    # Colour 19: 4% sRGB[75, 36, 49]    -> LAB[20, 20, 0] - good
    # Colour 20: 4% sRGB[81, 35, 20]    -> LAB[20, 20, 20] - good
    # Colour 21: 4% sRGB[134, 81, 63]   -> LAB[40, 20, 20] - good
    # Colour 22: 4% sRGB[159, 63, 65]   -> LAB[40, 40, 19] - good
    # Colour 23: 4% sRGB[162, 62, 29]   -> LAB[40, 40, 40] - good
    # Colour 24: 4% sRGB[223, 113, 76]  -> LAB[60, 40, 40] - good
    # Colour 25: 4% sRGB[249, 90, 78]   -> LAB[60, 60, 40] - good

    # All colours meets the primary requirements threshold

    algorithm = nieves2020.Nieves2020CentredCubes()
    recoloured_image, colour_palette, relative_frequencies = algorithm.generate_colour_palette(image)

    # Convert colour_palette to list
    colour_palette = [list(colour) for colour in colour_palette]

    # Check values found
    assert [0, 0, 0] in colour_palette  # Colour 1
    assert [48, 48, 48] in colour_palette  # Colour 2
    assert [94, 94, 94] in colour_palette  # Colour 3
    assert [145, 145, 145] in colour_palette  # Colour 4
    assert [198, 198, 198] in colour_palette  # Colour 5
    assert [255, 255, 255] in colour_palette  # Colour 6

    assert [244, 184, 162] in colour_palette  # Colour 7
    assert [180, 208, 121] in colour_palette  # Colour 8
    assert [135, 218, 119] in colour_palette  # Colour 9
    assert [0, 240, 196] in colour_palette  # Colour 10
    assert [0, 238, 255] in colour_palette  # Colour 11
    assert [136, 154, 0] in colour_palette  # Colour 12

    assert [103, 155, 144] in colour_palette  # Colour 13
    assert [255, 72, 0] in colour_palette  # Color 14
    assert [19, 163, 144] in colour_palette  # Colour 15
    assert [0, 69, 0] in colour_palette  # Colour 16
    assert [0, 71, 107] in colour_palette  # Colour 17
    assert [0, 79, 205] in colour_palette  # Colour 18

    assert [75, 36, 49] in colour_palette  # Colour 19
    assert [81, 35, 20] in colour_palette  # Colour 20
    assert [134, 81, 63] in colour_palette  # Colour 21
    assert [159, 63, 65] in colour_palette  # Colour 22
    assert [162, 62, 29] in colour_palette  # Colour 23
    assert [223, 113, 76] in colour_palette  # Colour 24
    assert [249, 90, 78] in colour_palette  # Colour 25

    # Check relative frequencies
    assert 0.04 == relative_frequencies[colour_palette.index([0, 0, 0])]  # Colour 1
    assert 0.04 == relative_frequencies[colour_palette.index([48, 48, 48])]  # Colour 2
    assert 0.04 == relative_frequencies[colour_palette.index([94, 94, 94])]  # Colour 3
    assert 0.04 == relative_frequencies[colour_palette.index([145, 145, 145])]  # Colour 4
    assert 0.04 == relative_frequencies[colour_palette.index([198, 198, 198])]  # Colour 5
    assert 0.04 == relative_frequencies[colour_palette.index([255, 255, 255])]  # Colour 6

    assert 0.04 == relative_frequencies[colour_palette.index([244, 184, 162])]  # Colour 7
    assert 0.04 == relative_frequencies[colour_palette.index([180, 208, 121])]  # Colour 8
    assert 0.04 == relative_frequencies[colour_palette.index([135, 218, 119])]  # Colour 9
    assert 0.04 == relative_frequencies[colour_palette.index([0, 240, 196])]  # Colour 10
    assert 0.04 == relative_frequencies[colour_palette.index([0, 238, 255])]  # Colour 11
    assert 0.04 == relative_frequencies[colour_palette.index([136, 154, 0])]  # Colour 12

    assert 0.04 == relative_frequencies[colour_palette.index([103, 155, 144])]  # Colour 13
    assert 0.04 == relative_frequencies[colour_palette.index([255, 72, 0])]  # Colour 14
    assert 0.04 == relative_frequencies[colour_palette.index([19, 163, 144])]  # Colour 15
    assert 0.04 == relative_frequencies[colour_palette.index([0, 69, 0])]  # Colour 16
    assert 0.04 == relative_frequencies[colour_palette.index([0, 71, 107])]  # Colour 17
    assert 0.04 == relative_frequencies[colour_palette.index([0, 79, 205])]  # Colour 18

    assert 0.04 == relative_frequencies[colour_palette.index([75, 36, 49])]  # Colour 19
    assert 0.04 == relative_frequencies[colour_palette.index([81, 35, 20])]  # Colour 20
    assert 0.04 == relative_frequencies[colour_palette.index([134, 81, 63])]  # Colour 21
    assert 0.04 == relative_frequencies[colour_palette.index([159, 63, 65])]  # Colour 22
    assert 0.04 == relative_frequencies[colour_palette.index([162, 62, 29])]  # Colour 23
    assert 0.04 == relative_frequencies[colour_palette.index([223, 113, 76])]  # Colour 24
    assert 0.04 == relative_frequencies[colour_palette.index([249, 90, 78])]  # Colour 25

    assert len(colour_palette) == 25


def test_closest_relevant_colour_used_to_recolour_pixel():
    image = helperfunctions.get_image("./colourpaletteextractor/tests/testImages/2-beige-10-sand-88-blue.png")
    # Colour 1:  2%  sRGB[186, 130, 110] -> LAB[60, 20, 20]
    # Colour 2:  10% sRGB[209, 198, 161] -> LAB[80, 0, 20]
    # Colour 3:  88% sRGB[0, 67, 139]    -> LAB[20, -60, -60]
    # Colour 1 is not relevant
    # Colour 2 is relevant according to the primary requirements
    # Colour 3 is relevant according to the primary requirements
    # Colour 1 will be replaced with the closest colour - Colour 2

    algorithm = nieves2020.Nieves2020CentredCubes()
    recoloured_image, colour_palette, relative_frequencies = algorithm.generate_colour_palette(image)

    # Convert colour_palette to list
    colour_palette = [list(colour) for colour in colour_palette]

    assert len(colour_palette) == 2

    # Check values found
    assert [209, 198, 161] in colour_palette  # Colour 2
    assert [0, 67, 139] in colour_palette  # Colour 3

    # Check relative frequencies
    assert 0.12 == relative_frequencies[colour_palette.index([209, 198, 161])]  # Colour 2
    assert 0.88 == relative_frequencies[colour_palette.index([0, 67, 139])]  # Colour 3

    # Check recoloured image has been recoloured correctly
    assert (recoloured_image[3][19][:] == [209, 198, 161]).all  # row then column
    assert (recoloured_image[2][19][:] == [209, 198, 161]).all

    assert (recoloured_image[0][0][:] == [209, 198, 161]).all
    assert (recoloured_image[0][1][:] == [209, 198, 161]).all
    assert (recoloured_image[0][2][:] == [209, 198, 161]).all
    assert (recoloured_image[0][3][:] == [209, 198, 161]).all
    assert (recoloured_image[0][4][:] == [0, 67, 139]).all

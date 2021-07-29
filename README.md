# ColourPaletteExtractor

ColourPaletteExtractor is a simple tool to generate the colour palette of an image. Built using Python, it can be used
on a computer running either Windows 10, or a Mac running macOS Mojave (10.14) or later. While the macOS version *may*
run on a computer running a Linux operating system, there is no guarantee that it will work; it is recommended that the
is compiled from the source code.


## 1) Licencing
    ColourPaletteExtractor Copyright (C) 2021  Tim Churchfield
    This program comes with ABSOLUTELY NO WARRANTY; for details see LICENCE.md.
    This is free software, and you are welcome to redistribute it
    under certain conditions; see LICENCE.md for details.


## 2) Download Instructions

The latest version of ColourPaletteExtractor can be obtained from
[GitHub](https://github.com/PurpleCrumpets/MSc-CS-Project---ColourPaletteExtractor/releases). Download the ```zip``` 
file that best matches your computer's operating system (found under ```Assets```) and extract its contents to a suitable
folder. For macOS, simply double-click the ```ColourPaletteExtractor``` application to open it. On Windows 10, open 
the ```ColourPaletteExtractor``` folder and double-click the ```ColourPaletteExtractor.exe``` executable file.


### 2.1) macOS Specifics

On opening the application for the first time on macOS, you may be met with a pop-up stating: 
```“ColourPaletteExtractor” can’t be opened because Apple cannot check it for malicious software.``` This is because the
application has not been signed and so Apple (arguably quite rightly) does not let you run it without an additional
hurdle. 

To allow for the application to be run, open ```System Preferences > Security & Privacy > General```. Make sure
that the setting for ```Allow apps downloaded from:``` is set to ```App Store and identified developers``` and click 
```Open Anyway``` for ```ColourPaletteExtractor```. 


### 2.2) Windows 10 Specifics

On Windows 10, you anti-virus software may decide to quarantine the ```ColourPaletteExtractor.exe``` file to check that
it is safe to use. This may take a while and prevent the application from running. Either add the folder containing the
application to your anti-virus' whitelist or disable your anti-virus whilst using the application. **Please** remember 
to turn it back on once you have finished! You may also need to run the application as an administrator.


### 2.3) Uninstalling

To uninstall the application, simply delete the folder and its contents that you downloaded in Section 2.

ColourPaletteExtractor also creates a settings file, ```ColourPaletteExtractor.ini```, that is used to store your 
preferences between uses. This is not automatically removed when you delete the application and should be manually
deleted.

On macOS, this file can be found at the following path; simply delete the ```The University of St Andrews```
folder and its contents.

      /Users/YOUR_USERNAME/.config/The University of St Andrews/ColourPaletteExtractor.ini

On Windows 10, the same settings file can be found at:

      C:\Users\YOUR_USERNAME\AppData\Roaming\The University of St Andrews\ColourPaletteExtractor.ini


## 3) Operating Instructions

Upon opening the application, you will be greeted with a simple quick start guide. This explains how to
obtain the colour palette of an image, as well as how to generate a report that summarises this information. 
It is also possible to analyse multiple images simultaneously; options to generate the colour palette for all open
images and their summary reports can be found under the *view* menu of the application.

The recoloured image is created by reassigning each pixel's colour to the most representative colour found in the colour
palette. For the algorithm proposed by Nieves et al. (2020), this is the colour in the colour palette that is closest to
the pixel's colour in the CIELAB colour space (the shortest Euclidean distance). The graph above shows the relative
frequency of the colours in the colour palette when used to recolour the original image. On the X-axis, each label
refers to the colour's sRGB triplet.

The time required to generate the colour palette of an image is directly proportional to the dimensions of the image.
It can take upwards of several minutes to obtain the colour palette of high resolution images. If multiple images are to be
anaylsed, it may be beneficial to reduce the resolution of the images to reduce the time required to process them. 
However, this may affect the make-up of the colour palette, as well as the relative frequency of each colour
in the recoloured image.

![Quick Start Guide](./colourpaletteextractor/view/resources/images/how-to-dark-mode.png)

### 3.1) Using with Python

While the application itself can be used to process multiple image simultaneously, it may be preferable to use the 
algorithm that generates the colour palette as part of your own Python script. The ```model.py``` module has a simple
function, ```generate_colour_palette_from_image```, that can be used for this purpose. It can take two parameters, the
file path to the image to be analysed (compulsory), and the name of the algorithm's Python class (optional). By default,
the ```Nieves2020CentredCubes``` algorithm is used (see the [source paper](https://doi.org/10.1364/AO.378659) 
for more information). Alternative algorithms can be found in the ```colourpaletteextractor.model.algorithms``` package.

If you wish to use this function, please make sure
that you have installed Python 3.9 or later, as well as the Python packages listed in the ```requirements.txt```
[file](https://github.com/PurpleCrumpets/MSc-CS-Project---ColourPaletteExtractor/blob/master/requirements.txt). It
may also be desirable to install these packages under a new Python virtual environment to prevent any conflicts with 
other packages you may have installed. 

A sample script, ```colourpaletteextractor/examples/generatecolourpaletteexample.py```, is provided that shows
how this can be achieved. It returns the recoloured image using only the colours found in the colour palette, the 
colour palette itself, and the relative frequencies of these colours in the recoloured image. To run this script, 
activate your new Python virtual environment, navigate to the ```ColourPaletteExtractor``` folder and use the following
command to run the script:

      python3 -m colourpaletteextractor.examples.generatecolourpaletteexample


### 3.2) Source Code Documentation

A set of [HTML files](https://github.com/PurpleCrumpets/MSc-CS-Project---ColourPaletteExtractor/tree/master/docs/build/html)
have been produced to support the future develop and maintenance of ```ColourPaletteExtractor```. These can be found in
the ```ColourPaletteExtractor/docs/build/html``` directory. The ```index.html``` contains the documentation homepage.



## 4) Compiling Instructions

To build the ```ColourPaletteExtractor``` application from the source code, it is highly recommended that a new
Python virtual environment is set-up. This will allow for the minimum number of Python packages to be installed, 
reducing the size of the resultant application. Please install the Python packages listed in the ```requirements.txt```
[file](https://github.com/PurpleCrumpets/MSc-CS-Project---ColourPaletteExtractor/blob/master/requirements.txt). Also 
note that the ```Sphinx```, ```sphinx-rtd-theme``` and ```pytest``` packages are only required if you wish to rebuild the
documentation (the two Sphinx packages) or run the test suite for the implemented algorithms (the latter package).


The ```create_executables.sh``` and ```create_executables.bat``` files are used to build the application for macOS
and Windows 10, respectively. These need to be modified to contain the path to your new Python virtual environment.
For the ```create_executables.sh``` bash script, please update ```Line 24``` to reflect this new path. ```Line 27```
also needs to be updated to specify the output directory you wish to use for the compiled application.

      Line 24  --> source /path/to/my/Python/virtual/environment/bin/activate

      Line 27 --> OUTPUT_DIR=/path/to/my/output/directory/for/the/ColourPaletteExtractor-Executables

For the ```create_executables.bat``` batch script, please update ```Line 27``` and ```Line 30``` to the path to the
Python virtual environment (**not** the *activate.bat* file) and the output directory, respectively.

      Line 27 --> set \path\to\my\Python\virtual\environment

      Line 30 --> set OUTPUT_DIR=\path\to\my\output\directory\for\the\ColourPaletteExtractor-Executables

Once updated, please make sure that the relevant permissions have been set to allow for these script to be run (i.e.,
```chmod 755 create_executables.sh```). Navigate
to them using the terminal on macOS, or the command prompt on Windows 10 and run these files. If all goes well, you
should find the compiled applications inside the ```dist``` folder of ```ColourPaletteExtractor-Executables```. 


### 4.1) Compiling Code Documentation

Additional documentation for the source code is available as a set of 
[HTML files](https://github.com/PurpleCrumpets/MSc-CS-Project---ColourPaletteExtractor/tree/master/docs/build/html). 
On macOS, the ```create_documentation.sh``` script can be used to recompile the documentation. As with the
application build scripts discussed in Section 4, ```Line 24``` of the ```create_documentation.sh``` script needs to be updated to
reflect the path to your Python virtual environment:

      Line 24  --> source /path/to/my/Python/virtual/environment/bin/activate

Navigate to the ```ColourPaletteExtractor``` directory and run the script, making sure that the script has
the appropriate execution permissions as discussed before in relation to the application build scripts.

## 5) Implementing a New Algorithm

Implementing a new algorithm is relatively straight-forward, with most of the infrastructure already in place. Please
follow the instructions below to add a new algorithm to the application.

1) Create a new subclass of ```PaletteAlgorithm``` in a new module ```mymodule.py``` of the ```algorithms``` package 
   using the following template:
   
```python
class MyNewAlgorithm(palettealgorithm.PaletteAlgorithm):

    name = "Boggis, Bunce and Bean (1970)"
    url = "www.a-lovely-link-to-my-algorithm.com"

    def __init__(self):
        """Constructor."""
        super().__init__(MyNewAlgorithm.name, MyNewAlgorithm.url)

    # Add any further code here that you require...

    def generate_colour_palette(self, image: np.array) -> tuple[Optional[np.array], list, list]:

        # Generate the colour palette for the image here
      
        # Set the initial progress
        self._set_progress(0)  # Initial progress = 0%
        if not self._continue_thread:
            return None, [], []
      
      
        # Increment the progress by a fixed amount
        self._increment_progress(increment_percent)
        if not self._continue_thread:
            return None, [], []
      
      
        # Set the final progress   
        self._set_progress(100)  # Final progress = 100%
        if not self._continue_thread:
            return None, [], []
      
        return recoloured_image, colour_palette, relative_frequencies

```
      

Please specify a ```name``` for the algorithm and a ```url``` to a valid website or file to allow for users to learn more
about how your algorithm works. The ```MyNewAlgorithm``` class inherits the abstract method ```generate_colour_palette```
from the abstract ```PaletteAlgorithm``` class. The ```image``` object is an ```np.array``` representing the image
to be analysed. It is either an [x, y, 3] or [x, y, 4] matrix, with the third dimension representing the red, 
green and blue colour channels of the 8-bit sRGB colour space. The fourth channel may sometimes occur if the image
has a transparency layer (e.g., some PNG images) and may need to be removed depending on your approach to generating the
colour palette.

The output from the method should be an ```np.array``` representing the recoloured image using only colours in the
colour palette, the list of RGB triplets, each represented by an ``np.array``, and the list of relative frequencies 
of each colour in the colour palette as found in the recoloured image stored as a ```float```. 

2) Add the following import statement for the new module ```mymodule.py``` to the top of the ```model.py``` module so
   the new algorithm can be picked up by the GUI and added as a new algorithm in the settings panel.
   
        from colourpaletteextractor.model.algorithms import mymodule


### 5.1) Adding Progress Bar Updates

While not technically necessary, it may be desirable to provide progress updates for the user while the colour palette
is being generated. The ```PaletteAlgorithm``` class provides two methods that can be used for this purpose, 
```_set_progress``` and ```_increment_progress``` (see the above example). The former method can be used to set the percentage progress
to a fixed amount (no more than 100%). The latter can be used to increase the progress bar by a certain
number of percentage points. This may be useful in a loop scenario, where a set progress percentage for a particular
loop can be divided up over the loop. 

By updating the progress bar, the execution status set by the user is also checked. By adding the following two
lines of code underneath any progress bar update (see the example above for how it could be used), the 
generation of the colour palette to be gracefully cancelled by the user.

      if not self._continue_thread:
        return None, [], []


### 5.2) Changing the Default Algorithm
Changing the default algorithm used by ```ColourPaletteExtractor``` is very straightforward, requiring two
small changes to the ```ColourPaletteExtractorModel``` class (found in the ```model``` module). To set the default
to your new algorithm, edit the ```DEFAULT_ALGORITHM``` static variable of the ```ColourPaletteExtractorModel``` class to your new 
algorithm:

      class ColourPaletteExtractorModel:
         DEFAULT_ALGORITHM = mymodule.MyNewAlgorithm


Note: This is the name of the class, *not* an instance of the class!

# ColourPaletteExtractor

ColourPaletteExtractor is a simple tool to generate the colour palette of an image. Built using Python, it can be used
on a computer running either Windows 10, or a Mac running macOS Mojave (10.14) or later. While the macOS version *may*
run on a computer running a Linux operating system, there is no guarantee that it will work; it is recommended that the
is compiled from the source code.

## 1) Licencing
    ColourPaletteExtractor Copyright (C) 2020  Tim Churchfield
    This program comes with ABSOLUTELY NO WARRANTY; for details see LICENCE.md.
    This is free software, and you are welcome to redistribute it
    under certain conditions; see LICENCE.md for details.

## 2) Download Instructions

The latest version of ColourPaletteExtractor can be obtained from
[GitHub](https://github.com/PurpleCrumpets/MSc-CS-Project---ColourPaletteExtractor/releases). Download the ```zip``` 
file that best matches your computer's operating system (found under ```Assets```) and extract its contents to a suitable
folder. For macOS, simply double-click the ```ColourPaletteExtractor``` application to open it. On Windows 10, open 
the ```ColourPaletteExtractor``` folder and double-click the ```ColourPaletteExtractor.exe``` executable file.


### 2.1) MacOS Specifics

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

         python3 -m colourpaletteextractor.examples.generatecolourpaletteexample.py


## 4) Compiling Instructions

### Set-up a New Virtual Python Environment


create a new virtual python environment
install the package requirements using the

### MacOS

Using

### Windows


## 5) Implementing a New Algorithm

Implementing a new algorithm is relatively straight-forward, with most of the infrastructure already in place.

1) Create a new subclass of ```PaletteAlgorithm``` in a new module ```mymodule.py``` of the ```algorithms``` package 
   using the following template:
   
        class MyNewAlgorithm(palettealgorithm.PaletteAlgorithm)
   
            name = "Boggis, Bunce and Bean (1970)"
            url = "www.a-lovely-link-to-my-algorithm.com"
   
            def __init__(self):
            """Constructor."""
                super().__init__(MyNewAlgorithm.name, MyNewAlgorithm.url)

                # Add further code here...

            def generate_colour_palette(self, image) -> tuple[ , list[]]:
                
                # Generate the colour palette here
                # You can make frequent call-backs to ... TODO
                
                return recoloured_image, colour_palette


Explain what the input and output variables are/should be

2) Add the following import statement for the new module ```mymodule.py``` to the top of the ```model.py``` module so
   the new algorithm can be picked up by the GUI and added as a new algorithm in the settings panel.
   
        from colourpaletteextractor.model.algorithms import mymodule


### 5.1) Adding Progress Bar Updates

It may be desirable to provide progress updates for the user while the colour palette is generated. There are two
   functions that can be used for this purpose:

This also allows for the generation of the colour palette to be gracefully cancelled by the user at this point


### Changing the Default Algorithm
To change the default algorithm used by the application, edit the ```DEFAULT_ALGORITHM``` static variable of the
   ```PaletteAlgorithm``` class to read the new algorithm sub-class class:
   
      class ColourPaletteExtractorModel:
         DEFAULT_ALGORITHM = mymodule.MyNewAlgorithm


Note: This is the name of the class, *not* an instance of the class! 



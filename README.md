# Extraction Dynamic Colour Palettes from Paintings

## Add licencing and other such stuff here, version number etc.


## Licencing
    ColourPaletteExtractor Copyright (C) 2020  Tim Churchfield
    This program comes with ABSOLUTELY NO WARRANTY; for details see LICENCE.md.
    This is free software, and you are welcome to redistribute it
    under certain conditions; see LICENCE.md for details.


## Using ColourPaletteExtractor

### Using the model API
The model using in this application supports a very simple API that can be used to obtain the
colour palette of an image when provided with its path. May end up adding percentages as a tuple
as well??



### Switching between Algorithms
Alternative algorithms may be implemented in the future.

## 2) Compiling Instructions

### macOS

### Windows


## 3) Implementing a New Algorithm

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


### Adding Progress Bar Updates

It may be desirable to provide progress updates for the user while the colour palette is generated. There are two
   functions that can be used for this purpose:


### Changing the Default Algorithm
To change the default algorithm used by the application, edit the ```DEFAULT_ALGORITHM``` static variable of the
   ```PaletteAlgorithm``` class to read the new algorithm sub-class class:
   
      class ColourPaletteExtractorModel:
         DEFAULT_ALGORITHM = mymodule.MyNewAlgorithm


Note: This is the name of the class, *not* an instance of the class! 


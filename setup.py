import numpy as np
from setuptools import setup, Extension
from Cython.Build import cythonize
import Cython.Compiler.Options
Cython.Compiler.Options.annotate = True

setup(
    name='ColourPaletteExtractor',
    ext_modules=cythonize((
        Extension("colourpaletteextractor.model.algorithms.nieves2020cython",
                  sources=["colourpaletteextractor/model/algorithms/nieves2020cython.pyx"], include_dirs=[np.get_include()],
                  define_macros=[("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION")],),), annotate=True),
    zip_safe=False
)

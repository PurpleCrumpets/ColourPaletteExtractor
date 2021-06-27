from setuptools import setup, Extension
from Cython.Build import cythonize

ext = Extension("nieves2020cython", sources=["nieves2020cython.pyx"])

setup(
    name='ColourPaletteExtractor',
    ext_modules=cythonize("colourpaletteextractor/model/algorithms/nieves2020cython.pyx"),
    zip_safe=False,
)

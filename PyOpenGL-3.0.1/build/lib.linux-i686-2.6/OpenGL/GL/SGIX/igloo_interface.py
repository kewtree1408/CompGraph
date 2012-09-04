'''OpenGL extension SGIX.igloo_interface

This module customises the behaviour of the 
OpenGL.raw.GL.SGIX.igloo_interface to provide a more 
Python-friendly API

The official definition of this extension is available here:
http://www.opengl.org/registry/specs/SGIX/igloo_interface.txt
'''
from OpenGL import platform, constants, constant, arrays
from OpenGL import extensions, wrapper
from OpenGL.GL import glget
import ctypes
from OpenGL.raw.GL.SGIX.igloo_interface import *
### END AUTOGENERATED SECTION
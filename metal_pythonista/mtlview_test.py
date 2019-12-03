from mtlviewer import MtlViewer
from seekbarview import SeekBarView
import ctypes


my_view = MtlViewer(frame=(0,0,414,414), background_color=(0,.3,0,1))
my_view.load_shader('./shader.metal.js')
seek_bar_view = SeekBarView(frame=(0, 0, 410, 34*2))
my_view.add_subview(seek_bar_view)
my_view.py_shader_config['flagment']['args'][0] = (seek_bar_view.get_playing_time, ctypes.c_float)
my_view.present('fullscreen', hide_title_bar=False)

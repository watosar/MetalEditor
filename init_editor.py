import setupui
from getfilepath import get_filepath
import mtlviewer.initialize
import pathlib
import configparser
import re
import sys
#import logger

root = setupui.setup()
if not root:
    setupui.root_view.viewWithTag_(-5).removeFromSuperview()
    exit()

shader_path = get_filepath() #and 'sampleShader.metal.js'
mtl_view, controller_view = mtlviewer.initialize.ready(pathlib.Path(shader_path))

tev = root.viewWithTag_(-1)
controller_view.will_draw = lambda : tev.setAlpha_(1) if tev.currentKeyboardHeight() else tev.setAlpha_(0.15)
tevd = tev.delegate()

def get_text():
    return str(tev.textView().text())

pattern = re.compile('/[*](.*?)[*]/', flags=re.S)
def get_config():
    match = pattern.match(get_text())
    if not match: return
    config_text = match[1]
    config = configparser.ConfigParser()
    config.read_string(config_text)
    return config

def set_config():
    global config
    config = get_config()
    if not config: return
    
    if 'Editor' in config:
        editor = config['Editor']
        try:
            fps = editor.getint('fps')
            if fps is not None:
                if fps <= 0: raise ValueError
                mtl_view.objc_mtkview.preferredFramesPerSecond = fps
        except ValueError as e:
            sys.stderr.write('fps value must be positive int')
        try:
            timer_limit = editor.getfloat('timer_limit')
            if timer_limit is not None:
                controller_view.seekbar_view.update_limit(timer_limit)
        except ValueError as e:
            sys.stderr.write('timer_limit value must be float')
    if 'Vertex' in config:
        vertex = config['Vertex']
        try:
            count = vertex.getint('count')
            if count is not None:
                mtl_view.py_shader_config['vertex']['count'] = count
        except ValueError as e:
            sys.stderr.write('count value must be int')
        try:
            primitive_type = vertex.getint('type')
            if primitive_type is not None:
                mtl_view.py_shader_config['vertex']['PrimitiveType'] = primitive_type
        except ValueError as e:
            sys.stderr.write('count value must be int')
    
def will_reload():
    tevd.willCloseTab()
    tevd.saveData()
    
def did_reload():
    set_config()

controller_view.will_reload = will_reload
controller_view.did_reload = did_reload
main = root.viewWithTag_(-2)
main.addSubview_(mtl_view)
tevp = root.viewWithTag_(-1).superview()
tevp.addSubview_(controller_view)
controller_view.objc_instance.setTag_(-5)

#set FPS
mtl_view.objc_mtkview.preferredFramesPerSecond = 30

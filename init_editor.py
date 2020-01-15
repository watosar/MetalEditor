import setupui
import mtlviewer.initialize
from pathlib import Path
import configparser
import re
import sys
import editor
from objc_util import *
#import logger
NSNotificationCenter = ObjCClass('NSNotificationCenter')
defaNotiCenter = NSNotificationCenter.defaultCenter()

def KeyboardNotificationReceiver_onWillChangeFrame_(_self, _cmd, _frame):
    ...
    

KeyboardNotificationReceiver = create_objc_class(
    'KeyboardNotificationReceiver',
    methods = [KeyboardNotificationReceiver_onWillChangeFrame_]
)


class MetalEditor:
    def __init__(self, shader_path):
        self.shader_path = Path(shader_path) #and 'sampleShader.metal.js'
        mtl_view, controller_view = mtlviewer.initialize.ready(self.shader_path)
        
        self.mtl_view = mtl_view
        self.controller_view = controller_view
        self.tev = root.viewWithTag_(-1)
        
        mtlviewer.mtlview.renderer.get_shader_source = lambda *_: self.get_text()
        
        controller_view.will_draw = lambda *_, tev=self.tev: tev.setAlpha_(1) if tev.currentKeyboardHeight() else tev.setAlpha_(0.15)
        
        self.tevd = self.tev.delegate()
        controller_view.will_reload = self.will_reload
        controller_view.did_reload = self.did_reload
        
        self.baseView = root.viewWithTag_(-2)
        controller_view.objc_instance.setTag_(-5)
        
        #swizzle editor didChange for incremental update
        
    def will_reload(self):
        self.tevd.willCloseTab()
        self.tevd.saveData()
        
    def did_reload(self):
        #print('reload')
        self.set_config()
    
    def start(self):
        self.baseView.addSubview_(self.mtl_view.objc_instance)
        tevp = self.tev.superview()
        tevp.addSubview_(self.controller_view)
        
        self.mtl_view.objc_mtkview.preferredFramesPerSecond = 30
        self.did_reload()
        
    def get_text(self):
        return str(self.tev.textView().text())
    
    pattern = re.compile('/[*](.*?)[*]/', flags=re.S)
    def get_config(self):
        match = self.pattern.match(self.get_text())
        if not match: return
        config_text = match[1]
        config = configparser.ConfigParser()
        config.read_string(config_text)
        return config

    def set_config(self):
        config = self.get_config()
        mtl_view = self.mtl_view
        controller_view = self.controller_view
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

    def _editorDidChange_(self, textview_pointer):
        ...
        # call original
    
    def editor_did_change(self):
        ...

res = setupui.setup()
if not res:
    if setupui.rootView.viewWithTag_(-1):
        setupui.rootView.viewWithTag_(-5).removeFromSuperview()
    else:
        name = str(setupui.rootView.viewWithTag_(-2).subviews()[0].name())
        sys.stderr.write(f'editor is already working for {name}\n')
    exit()
root = res
    
if __name__ == '__main__':
    file_path = editor.get_path()
    mtl_editor = MetalEditor(file_path)
    mtl_editor.start()
    
    #editor.mtl_view.objc_mtkview.preferredFramesPerSecond = 0
    import save_image
    def save():
        save_image.clear_cache()
        save_image.save(editor.mtl_view.objc_mtkview)
    
    
'''
editor_tab. editorViewDidChange 
のswizzleで変更を取得できる説
'''

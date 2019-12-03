import ui
from objc_util import *
import ctypes
from . import viewcontroller
from . import renderer

class MtlViewer(ui.View):
    def __init__(self, *args, frame, **kwargs):
        super().__init__(*args, frame=frame, **kwargs)
        objc_cvc = viewcontroller.init(frame)
        self.objc_mtkview = objc_cvc.view()
        objc_self = ObjCInstance(self)
        objc_self.addSubview_(self.objc_mtkview)
        objc_cvc.didMoveToParentViewController_(objc_self)
    
    @on_main_thread
    def load_shader(self, sh_path):
        self.objc_mtkview.delegate = renderer.init(self.objc_mtkview, sh_path)
        self.py_shader_config = self.objc_mtkview.delegate().py_shader_config
        
    def will_close(self):
        print('----close----')


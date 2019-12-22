import ui
from objc_util import *
import ctypes
from . import viewcontroller
from . import renderer

class MtlView(ui.View):
    def __init__(self, *args, frame, **kwargs):
        super().__init__(*args, frame=frame, **kwargs)
        objc_cvc = viewcontroller.init(frame)
        self.objc_mtkview = objc_cvc.view()
        objc_self = ObjCInstance(self)
        objc_self.addSubview_(self.objc_mtkview)
        objc_cvc.didMoveToParentViewController_(objc_self)
    
    #@on_main_thread
    def load_shader(self, sh_path):
        #print('load', sh_path)
        resp = renderer.init(self.objc_mtkview, sh_path)
        if not resp:
            return 
        self.objc_mtkview.delegate, self.py_shader_config = resp
        return True
            
    def will_close(self):
        print('----close----')


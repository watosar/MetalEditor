import ui
from objc_util import *
from .seek_bar import SeekBarView
from .viewcontroller import ViewController,renderer

seek_bar_view = SeekBarView(frame=(0, 0, 410, 34*2))
renderer.get_time = seek_bar_view.get_playing_time


class MtlViewer(ui.View):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, frame=(0,0,414,414), **kwargs)
    
    @on_main_thread
    def load_shader(self, sh_path):
        cvc = ViewController.new()
        self.sceneview = cvc.view()
        self_objc = ObjCInstance(self)
        self_objc.addSubview_(self.sceneview)
        cvc.didMoveToParentViewController_(self_objc)
        
    def will_close(self):
        print('----close----')


if __name__ == '__main__':
    my_view = MtlViewer(background_color=(0,.3,0,1))
    my_view.load_shader(...)
    my_view.add_subview(seek_bar_view)
    my_view.present('fullscreen', hide_title_bar=False)


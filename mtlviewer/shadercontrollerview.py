import ui
import ctypes
from . import seekbarview

class ShaderControllerView(ui.View):
    def __init__(self, *args, shaderview, shaderpath, frame=(0, 0, 414, 68),  debug=False, **kwargs):
        super().__init__(name='ShaderControllerView', *args, frame=frame,  **kwargs)
        
        self.reload_button = ui.Button(name='reload', frame=(414-50,5,40,29), flex='LB', font=('<System>', 13.0))
        self.reload_button.image = ui.Image('iob:ios7_reload_256')
        self.add_subview(self.reload_button)
        
        self.appear_button = ui.Button(name='appear', frame=(414-50,39,40,29), flex='LT', font=('<System>', 13.0))
        self.appear_button.image = ui.Image('iob:chevron_down_256')
        self.appear_button.action = self.appear_action
        self.add_subview(self.appear_button)
        
        self.seekbar_view = seekbarview.SeekBarView(flex='RB')
        self.seekbar_view.width = 414-40
        self.add_subview(self.seekbar_view)
        
        self.reload_button.action = self.reload_action
        
        self.shaderview = shaderview
        self.shaderpath = shaderpath
        self.reload_action()
    
    def will_draw(self):
        return 
        
    def _on_draw(self) -> float:
        self.will_draw()
        return self.seekbar_view.get_playing_time()
    
    def will_reload(self):
        return 
        
    def reload_action(self, *_):
        self.will_reload()
        if self.shaderview.load_shader(self.shaderpath):
            self.shaderview.py_shader_config['flagment']['args'][0] = (self._on_draw, ctypes.c_float)
    
    def appear_action(self, *_):
        if not self.y < 0:
            self.y = -68
            self.height = 102
            self.appear_button.image = ui.Image('iob:chevron_up_256')
        else:
            self.y = 0
            self.height = 68
            self.appear_button.image = ui.Image('iob:chevron_down_256')


import ui
import time


class SeekBarView(ui.View):
    def __init__(self, *args, frame=(0, 0, 414, 68), **kwargs):
        super().__init__(name='SeekVarView', frame=frame)
        
        self.theme_color = (0.0392156862745098, 0.5176470588235295, 1.0, 1.0)
        
        self.seek_slider = ui.Slider(frame=(20, 0,414-40,34), flex='WB', name='seekbar')
        self.seek_slider.action = self.seek_action
        self.add_subview(self.seek_slider)
        
        self.play_button = ui.Button(name='play', frame=(20,34,40,30), flex='RB', font=('<System>', 13.0))
        self.play_button.image = ui.Image.named('iob:play_256')
        self.play_button.action = self.toggle_playing
        self.add_subview(self.play_button)
        
        self.loop_button = ui.Button(name='play', frame=(60,34,40,30), flex='RB', font=('<System>', 13.0), tint_color=(.3, .3, .3, 1))
        self.loop_button.image = ui.Image.named('iob:loop_256')
        self.loop_button.action = self.toggle_loop
        self.add_subview(self.loop_button)
        
        self.time_label = ui.Label(name='time', frame=(100,34,80,34), flex='RB', text='0.00/10.0', font=('<System>', 18.0), alignment=1, text_color=self.theme_color)
        self.add_subview(self.time_label)
        
        self._start =0
        self.limit = 10
        self.is_playing = False
        self.is_loop = False
    
    @property
    def playing_time(self):
        return self.seek_slider.value * self.limit
    
    def toggle_playing(self, *args):
        self.is_playing = not self.is_playing
        self.play_button.image = ui.Image.named('iob:{}_256'.format(('play','pause')[self.is_playing]))
        if self.is_playing:
            self._start = time.time() - self.playing_time
        
    def toggle_loop(self, *args):
        self.is_loop = not self.is_loop
        self.loop_button.tint_color = ((.3,.3,.3,1), self.theme_color)[self.is_loop]
        
    def update_time_presence(self):
        self.time_label.text = f'{str(self.playing_time)[:4]:<04}/10.0'
        
    def seek_action(self, *args):
        if self.is_playing: self.toggle_playing()
        if self.seek_slider.value is None: return 
        self._start = time.time() - self.playing_time
        self.update_time_presence()
    
    def get_playing_time(self):
        if self.is_playing: 
            seek_value = (time.time() - self._start) / self.limit
            if seek_value <= 1.0:
                pass
            elif not self.is_loop:
                self.toggle_playing()
                seek_value = 1
            else:
                self._start = time.time()
                seek_value = 0
            self.seek_slider.value = seek_value
            self.update_time_presence()
        return self.playing_time
        
        
if __name__ == '__main__':
    wrap = ui.View()
    sbv = SeekBarView(frame=(0, 0, 414, 68))
    wrap.add_subview(sbv)
    wrap.present()
    while sbv.on_screen:
        sbv.get_playing_time()
        time.sleep(0.2)


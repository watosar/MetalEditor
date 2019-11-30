import ui

class RenderController(ui.View):
    def keyboard_frame_did_change(self, frame):
        print(frame)
        
RenderController().present()

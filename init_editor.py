import setupui
import mtlviewer.initialize
import pathlib
import sys
import io
#sys.stdout = io.StringIO()
import time



if __name__ == '__main__':
    root = setupui.setup()
    if not root:
        setupui.root_view.viewWithTag_(-5).removeFromSuperview()
        exit()
    mtl_view, controller_view = mtlviewer.initialize.ready(pathlib.Path('./mtlviewer/shader.metal.js'))
    
    tev = root.viewWithTag_(-1)
    controller_view.will_draw = lambda : tev.setAlpha_(1) if tev.currentKeyboardHeight() else tev.setAlpha_(0.15)
    tevd = tev.delegate()
    controller_view.will_reload = lambda : tevd.saveData()
    main = root.viewWithTag_(-2)
    main.addSubview_(mtl_view)
    tevp = root.viewWithTag_(-1).superview()
    tevp.addSubview_(controller_view)
    controller_view.objc_instance.setTag_(-5)
    mtl_view.objc_mtkview.preferredFramesPerSecond = 30
    
'''
texteditorview delegate willclosetapb で saveかどうか調べる
'''

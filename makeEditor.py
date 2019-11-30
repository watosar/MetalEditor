# coding: utf-8
import logger
from objc_util import *
import ui
import sys


UIApplication = ObjCClass('UIApplication')


main_view=UIApplication.sharedApplication().keyWindow().rootViewController().view()

my_view = main_view.viewWithTag_(-1)

if my_view:
    my_view.removeFromSuperview()
    main_view.viewWithTag_(-2).removeFromSuperview()
    tev = main_view.viewWithTag_(-3)
    tev.alpha = 1
    exit()

from metal_pythonista.main import MtlViewer,seek_bar_view
    
def get_subview(view, description):
    vs=view.subviews()
    if vs is None:
        return None
    target = None
    for v in vs:
        if description in str(v.description()):
            return v
        target = get_subview(v, description)
        if target:
            return target

def make_mainView():
    myView = UIView.alloc().initWithFrame_(CGRect(CGPoint(0, 0), CGSize(414, 414)))
    myView.setAutoresizingMask_(18) #WH
    myView.setTag_(-1)
    myView.backgroundColor = UIColor.colorWithRed_green_blue_alpha_(1,0,0,1)
    
    return myView
    
def reload_action(sender):
    ...


def close_action(sender):
    print('action')
    spview = sender.superview
    is_open = spview.y
    spview.y = is_open * -68

def make_controllerView():
    controller_view = ui.View(frame=(0, 0, 414, seek_bar_view.height+34))
    side_buttons = ui.View(frame=(362, 0, 52, 68))
    reload_button = ui.Button(image=ui.Image('iob:ios7_reload_256'))
    reload_button.frame = (0, 0, 52, 34)
    reload_button.action = reload_action
    
    close_button = ui.Button(image=ui.Image('iob:arrow_up_b_256'), flex='RT', font=('<System>', 13.0), action=lambda *_:print('action'))
    close_button.frame = (0, 34, 52, 34)
    #close_button.action = close_action
    side_buttons.add_subview(reload_button)
    side_buttons.add_subview(close_button)
    
    seek_bar_view.frame = (15, 0, 360, seek_bar_view.height)
    seek_bar_view.flex = 'WT'
    
    controller_view.add_subview(seek_bar_view)
    controller_view.add_subview(side_buttons)
    
    wrap_view = ui.View(frame=controller_view.frame)
    wrap_view.add_subview(controller_view)
    cv = wrap_view.objc_instance
    cv.setTag_(-2)
    return cv


text_editor_view = get_subview(main_view,'OMTextEditorView')
text_editor_view.setTag_(-3)
text_editor_view.alpha = 0.8
text_editor_view_parent = text_editor_view.superview()


main = make_mainView()
mtl_viewer = MtlViewer(background_color=(0,.3,0,1)).objc_instance
main.addSubview_(mtl_viewer)
text_editor_view_parent.addSubview_(main)
text_editor_view_parent.sendSubviewToBack_(main)


controller_view = make_controllerView()
text_editor_view_parent.addSubview_(controller_view)

# coding: utf-8
import logger
from objc_util import *
import ui
import sys


def setup():
    UIApplication = ObjCClass('UIApplication')
    root_view=UIApplication.sharedApplication().keyWindow().rootViewController().view()
    
    my_view = root_view.viewWithTag_(-2)
    
    if my_view:
        my_view.removeFromSuperview()
        tev = root_view.viewWithTag_(-1)
        tev.alpha = 1
        return 'clearnup'
        
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
        myView.setTag_(-2)
        myView.backgroundColor = UIColor.colorWithRed_green_blue_alpha_(1,0,0,1)
        
        return myView
    
    
    text_editor_view = root_view.viewWithTag_(-1) or get_subview(root_view,'OMTextEditorView')
    text_editor_view.setTag_(-1)
    text_editor_view.alpha = 0.8
    text_editor_view_parent = text_editor_view.superview()
    
    
    main = make_mainView()
    #main.addSubview_(mtl_viewer)
    text_editor_view_parent.addSubview_(main)
    text_editor_view_parent.sendSubviewToBack_(main)
    return 'setup'

if __name__ == '__main__':
    setup()


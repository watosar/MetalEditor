# coding: utf-8
import logger
from objc_util import *
import ui
import sys


UIApplication = ObjCClass('UIApplication')
UIDeviceRGBColor = ObjCClass('UIDeviceRGBColor')
root_view=UIApplication.sharedApplication().keyWindow().rootViewController().view()


def get_subview(view, *, description=None, attribute=None):
    if not (description or attribute):
        raise ValueError('need description or attribute')
    vs=view.subviews()
    if vs is None: return None
    target = None
    for v in vs:
        if description and description in str(v.description()):
            return v
        elif attribute:
            value = None
            try:
                value = getattr(v, attribute['name'])()
                print(value)
                if attribute['value'] in str(value):
                    return v
            except AttributeError:
                pass
        target = get_subview(v, description=description, attribute=attribute)
        if target: return target
        

def get_filename():
    return str(get_subview(root_view, description=" ▾'""; ").text())[:-2]


def make_mainView():
    myView = UIView.alloc().initWithFrame_(CGRect(CGPoint(32, 0), CGSize(382, 382)))
    myView.setAutoresizingMask_(18) #WH
    myView.setTag_(-2)
    myView.backgroundColor = UIColor.colorWithRed_green_blue_alpha_(0.4, 1, 0.4, 1)
    return myView
    
def myEditingDelegate_textViewDidBeginEditing_(_self, _cmd, _):
    print('hi')
        
myEditingDelegate = create_objc_class( 
    'myEditingDelegate',
    superclass = NSObject,
    methods=[
        myEditingDelegate_textViewDidBeginEditing_,
    ],
    classmethods=[],
    protocols = ['UITextViewDelegate']
)
    

def setup():
    my_view = root_view.viewWithTag_(-2)
    
    if my_view:
        root_view.frameOrigine = CGPoint(0, 0)
        my_view.removeFromSuperview()
        tev = root_view.viewWithTag_(-1)
        tev.tintgroundColor = UIDeviceRGBColor.colorWithRed_green_blue_alpha_(0.176471, 0.176471, 0.176471, 1)
        tev.backgroundColor = UIDeviceRGBColor.colorWithRed_green_blue_alpha_(0.176471, 0.176471, 0.176471, 1)
        tev.alpha = 1
        return
    
    titlebar = get_subview(root_view, description=(" ▾'""; ")).superview().superview()
    titlebar.setTag_(-3)
    #titlebar.addSubview_(make_mainView())
    
    text_editor_view = root_view.viewWithTag_(-1) or get_subview(root_view, description='OMTextEditor''View')
    text_editor_view.setTag_(-1)
    text_editor_view.tintColor = UIDeviceRGBColor.clearColor()
    text_editor_view.backgroundColor = UIDeviceRGBColor.colorWithRed_green_blue_alpha_(0.176471, 0.176471, 0.176471, 0.4)
    text_editor_view.alpha = 0.8
    text_editor_view_parent = text_editor_view.superview()
    
    
    text_editor_view._viewDelegate = myEditingDelegate.new()
    
    main = make_mainView()
    #main.addSubview_(mtl_viewer)
    text_editor_view_parent.addSubview_(main)
    text_editor_view_parent.sendSubviewToBack_(main)
    return root_view 


if __name__ == '__main__':
    setup()
    pass


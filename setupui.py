# coding: utf-8
#import logger
from objc_util import *
import sys
import editor

UIApplication = ObjCClass('UIApplication')
NSMutableAttributedString = ObjCClass('NSMutableAttributedString')
UIDeviceRGBColor = ObjCClass('UIDeviceRGBColor')
rootView = UIApplication.sharedApplication().keyWindow().rootViewController().view()

EDITOR_VIEW_TAG = -1
BASE_VIEW_TAG = -2

def get_editorView():
    editorView = rootView.viewWithTag_(EDITOR_VIEW_TAG)
    if editorView: return editorView
    
    editorView = editor._get_editor_tab().editorView()
    editorView.setTag_(EDITOR_VIEW_TAG)
    return editorView


def get_theme_bgColor():
    col = editor.get_theme_dict()['background']
    return UIColor.colorWithHexString(col)
 
       
def reapply_editor_theme(): 
    editorView = get_editorView()
    bgColor = get_theme_bgColor()
    editorView.backgroundColor = bgColor
    editorView.alpha = 1
    editorView.superview().backgroundColor = bgColor
    

def make_baseView():
    width = rootView.frame().size.width
    myView = UIView.alloc().initWithFrame_(CGRect(CGPoint(32, 0), CGSize(width-32, width-32)))
    myView.setAutoresizingMask_(18) #WH
    myView.setTag_(BASE_VIEW_TAG)
    myView.backgroundColor = UIColor.colorWithRed_green_blue_alpha_(0.4, 1, 0.4, 1)
    return myView
    

@on_main_thread
def setup():
    baseView = rootView.viewWithTag_(BASE_VIEW_TAG)
    
    if baseView:
        tev = rootView.viewWithTag_(EDITOR_VIEW_TAG)
        if not tev:
            sys.stderr.write('cannot start more editor\n')
            return
        baseView.removeFromSuperview()
        reapply_editor_theme()
        return
    
    editor_view = get_editorView()
    
    editor_view.backgroundColor = get_theme_bgColor().colorWithAlphaComponent_(0.2)
    editor_view_s = editor_view.superview()
    editor_view_s.backgroundColor = UIColor.clearColor()
    editor_view_s_s = editor_view_s.superview()
    baseView = make_baseView()
    
    editor_view_s_s.addSubview_(baseView)
    editor_view_s_s.sendSubviewToBack_(baseView)
    
    return rootView

#exit()
if __name__ == '__main__':
    res = setup()
    ev = rootView.viewWithTag_(EDITOR_VIEW_TAG)
    '''
    import edit_theme
    if res:
        alpha = 'cc'
    else:
        alpha = '00'
    #edit_theme.set_text_background(tev, '000000'+alpha)
    '''
    pass



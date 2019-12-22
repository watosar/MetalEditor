# coding: utf-8

from objc_util import *

UIApplication = ObjCClass('UIApplication')
root_view=UIApplication.sharedApplication().keyWindow().rootViewController().view()

def get_subview(view, description):
    vs=view.subviews()
    if vs is None: return None
    target = None
    for v in vs:
        if description and description in str(v.description()):
            return v
        target = get_subview(v, description)
        if target: return target

def get_filepath():
    tevd = get_subview(root_view, 'OMText''EditorView').delegate()
    return str(tevd.filePath())
    
if __name__ == '__main__':
    print(get_filepath())

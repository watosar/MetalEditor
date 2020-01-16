import setupui
import mtlviewer.initialize
from pathlib import Path
import configparser
import re
import sys
import editor
from objc_util import *
from objc_util import parse_types
import objc_util
import ctypes
import logger
NSNotificationCenter = ObjCClass('NSNotificationCenter')
defaNotiCenter = NSNotificationCenter.defaultCenter()

method_exchangeImplementations=c.method_exchangeImplementations
method_exchangeImplementations.restype=None
method_exchangeImplementations.argtypes=[c_void_p,c_void_p]

method_setImplementation=c.method_setImplementation
method_setImplementation.restype=None
method_setImplementation.argtypes=[c_void_p, c_void_p]


class MetalEditor:
    def __init__(self, shader_path):
        self.shader_path = Path(shader_path) #and 'sampleShader.metal.js'
        mtl_view, controller_view = mtlviewer.initialize.ready(self.shader_path)

        self.mtl_view = mtl_view
        self.controller_view = controller_view
        self.tev = setupui.rootView.viewWithTag_(setupui.EDITOR_VIEW_TAG)

        mtlviewer.mtlview.renderer.get_shader_source = lambda *_: self.get_text()

        self.tevd = self.tev.delegate()
        controller_view.will_reload = self.will_reload
        controller_view.did_reload = self.did_reload
        controller_view.objc_instance.setTag_(-5)
        
        self.baseView = setupui.rootView.viewWithTag_(setupui.BASE_VIEW_TAG)
        

        self.swizzle_texteditor()
        self.set_kbobserver()

    def keyboardwillchangeframe(self, frame):
        if frame.size.height:
            self.tev.setAlpha_(1)
        else:
            self.tev.setAlpha_(0.15)

    def will_reload(self):
        self.tevd.willCloseTab()
        self.tevd.saveData()

    def did_reload(self):
        self.set_config()

    def start(self):
        self.baseView.addSubview_(self.mtl_view.objc_instance)
        tevp = self.tev.superview()
        tevp.addSubview_(self.controller_view)

        self.mtl_view.objc_mtkview.preferredFramesPerSecond = 30
        self.did_reload()

    def get_text(self):
        return str(self.tev.textView().text())

    pattern = re.compile('/[*](.*?)[*]/', flags=re.S)
    def get_config(self):
        match = self.pattern.match(self.get_text())
        if not match: return
        config_text = match[1]
        config = configparser.ConfigParser()
        config.read_string(config_text)
        return config

    def set_config(self):
        config = self.get_config()
        mtl_view = self.mtl_view
        controller_view = self.controller_view
        if not config: return

        if 'Editor' in config:
            editor = config['Editor']
            try:
                fps = editor.getint('fps')
                if fps is not None:
                    if fps <= 0: raise ValueError
                    mtl_view.objc_mtkview.preferredFramesPerSecond = fps
            except ValueError as e:
                sys.stderr.write('fps value must be positive int')
            try:
                timer_limit = editor.getfloat('timer_limit')
                if timer_limit is not None:
                    controller_view.seekbar_view.update_limit(timer_limit)
            except ValueError as e:
                sys.stderr.write('timer_limit value must be float')
        if 'Vertex' in config:
            vertex = config['Vertex']
            try:
                count = vertex.getint('count')
                if count is not None:
                    mtl_view.py_shader_config['vertex']['count'] = count
            except ValueError as e:
                sys.stderr.write('count value must be int')
            try:
                primitive_type = vertex.getint('type')
                if primitive_type is not None:
                    mtl_view.py_shader_config['vertex']['PrimitiveType'] = primitive_type
            except ValueError as e:
                sys.stderr.write('count value must be int')

    def _editorDidChange_(self, _self, _cmd, textview_pointer):
        if ObjCInstance(textview_pointer) == self.tev:
            self.tevd.originalEditorViewDidChange_(textview_pointer)
            self.editor_did_change()
        else:
            editor._get_editor_tab().originalEditorViewDidChange_(textview_pointer)
            
    @on_main_thread
    def swizzle_texteditor(self):
        #swizzle editor didChange for incremental update
        #refer: https://github.com/jsbain/objc_hacks/blob/master/swizzle.py
        type_encoding = self.tevd.editorViewDidChange_.encoding
        restype, argtypes, argtype_encodings = parse_types(type_encoding)
        IMPTYPE = ctypes.CFUNCTYPE(restype, *argtypes)
        imp = IMPTYPE(self._editorDidChange_)
        retain_global(imp)
        selector = 'editorViewDidChange:'
        new_sel = 'originalEditorViewDidChange:'
        cls=ObjCInstance(c.object_getClass(self.tevd.ptr))
        didAdd=c.class_addMethod(cls, sel(new_sel), imp, type_encoding)
        if didAdd:
            orig_method = c.class_getInstanceMethod(cls.ptr, sel(selector))
            new_method = c.class_getInstanceMethod(cls.ptr, sel(new_sel))
            method_exchangeImplementations(orig_method, new_method)
        else:
            # setimp,
            orig_method=c.class_getInstanceMethod(cls.ptr, sel(selector))
            method_setImplementation(orig_method, imp)

    def editor_did_change(self):
        self.mtl_view.load_shader(self.shader_path)
        
    def set_kbobserver(self):
        def kbObserver_didShow_(_self, _cmd, flg):
            if not flg: return 
            self.kb_did_show()
        kbObserver_didShow_.encoding = 'v@:B'
        
        def kbObserver_didHide_(_self, _cmd, flg):
            if not flg: return 
            self.kb_did_hide()
        kbObserver_didHide_.encoding = 'v@:B'
        
        kbObserver = create_objc_class(
            'kbObserver', 
            methods = [
                kbObserver_didShow_, kbObserver_didHide_
            ]
        )
        obs = kbObserver.new()
        retain_global(obs)
        for key in ('Show', 'Hide'):
            defaNotiCenter.addObserver_selector_name_object_(
                obs, sel(f'did{key}:'), f'UIKeyboardDid{key}Notification', None
            )
        
    def kb_did_show(self):
        self.tev.alpha = 1
    
    def kb_did_hide(self):
        self.tev.alpha = .15
        

res = setupui.setup()
if not res:
    if setupui.rootView.viewWithTag_(setupui.EDITOR_VIEW_TAG):
        setupui.rootView.viewWithTag_(-5).removeFromSuperview()
    else:
        name = str(setupui.rootView.viewWithTag_(setupui.BASE_VIEW_TAG).subviews()[0].name())
        sys.stderr.write(f'editor is already working for {name}\n')
    for i in objc_util._retained_globals:
        if 'kbObserver' in repr(i):
            release_global(i)
            defaNotiCenter.removeObserver_(i)
    exit()

if __name__ == '__main__':
    file_path = editor.get_path()
    mts_editor = MetalEditor(file_path)
    mts_editor.start()
    retain_global(mts_editor)
    
    import save_image
    def save():
        save_image.save(mts_editor.mtl_view.objc_mtkview)


'''
shaderのエラー表示をeditor.annotate_lineで行う
'''

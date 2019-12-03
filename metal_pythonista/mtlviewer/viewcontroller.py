import ctypes
from objc_util import *


load_framework('MetalKit')
MTKView = ObjCClass('MTKView')


MTLCreateSystemDefaultDevice = c.MTLCreateSystemDefaultDevice
MTLCreateSystemDefaultDevice.restype = c_void_p
def mtl_create_system_default_device():
    return ObjCInstance(MTLCreateSystemDefaultDevice())


def create_mtk_view(x, y, w, h):
    view = MTKView.alloc().initWithFrame_device_((CGRect(CGPoint(x, y), CGSize(w, h))), mtl_create_system_default_device())
    return view
    

def ViewController_viewDidLoad(_self, _cmd):
    print('did load')
    self = ObjCInstance(_self)
    self.view = view = create_mtk_view(0, 0, 414, 414)
    view.preferredFramesPerSecond = 60
    

UIViewController = ObjCClass('UIViewController')
ViewController = create_objc_class(
    'ViewController',
    superclass = UIViewController,
    methods=[
        ViewController_viewDidLoad,
    ]
)

def init(frame=(0, 0, 414, 414)):
    cvc = ViewController.new()
    cvc.view().frame = CGRect(CGPoint(*frame[:2]), CGSize(*frame[2:4]))
    return cvc


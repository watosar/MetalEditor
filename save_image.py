from ctypes import *
import objc_util
from objc_util import *
import logger

load_framework('Metal')

def structure(cls):
    return type(cls.__name__, (Structure,), {'_fields_':[(name,)+(ann if isinstance(ann, (tuple,)) else (ann,)) for name, ann in cls.__annotations__.items()]})

@structure
class MTLOrigin:
    x: c_ulonglong
    y: c_ulonglong
    z: c_ulonglong
    
@structure
class MTLSize:
    width: c_ulonglong
    height: c_ulonglong
    depth: c_ulonglong

@structure
class MTLRegion:
    orogin: MTLOrigin
    size: MTLSize


malloc = c.malloc
malloc.restype = c_void_p

CGColorSpaceCreateDeviceRGB = c.CGColorSpaceCreateDeviceRGB
CGDataProviderCreateWithData = c.CGDataProviderCreateWithData
CGImageCreate = c.CGImageCreate
CGImageCreate.restype = c_void_p
CGImageCreate.argtypes = [c_size_t, c_size_t, c_size_t, c_size_t, c_size_t, c_void_p, c_uint32, c_void_p, c_void_p, c_bool, c_int32]
CGColorSpaceCreateDeviceRGB.restype = c_void_p
CGDataProviderCreateWithData.restype = c_void_p



def MTLRegionMake2D(x, y, width, height):
    return MTLRegion(MTLOrigin(x, y, 0), MTLSize(width, height, 1))
    
kCGBitmapByteOrder32Little = 2 << 12
kCGImageAlphaFirst = 0
kCGRenderingIntentDefault = 0
objc_util.type_encodings['{MTLRegion}'] = MTLRegion

@on_main_thread
def save(mtkview):
    mtkview.framebufferOnly = False
    texture = mtkview.currentDrawable().texture()
    width = texture.width()
    height = texture.height()
    rowBytes = width * 4
    selftruesize = width * height * 4
    p = malloc(selftruesize)
    
    func = texture.getBytes_bytesPerRow_fromRegion_mipmapLevel_
    func.encoding = b'v88@0:8^v16Q24{MTLRegion}32Q80'
    
    func(
        p, rowBytes, MTLRegionMake2D(0, 0, width, height), 0
    )
    
    colorSpace = CGColorSpaceCreateDeviceRGB()
    bitmapInfo = kCGBitmapByteOrder32Little | kCGImageAlphaFirst
    
    provider = CGDataProviderCreateWithData(None, c_void_p(p), c_size_t(selftruesize), None)
    
    cgImageRef = CGImageCreate(
        width, height, 8, 32, rowBytes, 
        colorSpace, bitmapInfo, provider, 
        None, True, kCGRenderingIntentDefault
    )
    
    ui_image = UIImage.imageWithCGImage_(ObjCInstance(cgImageRef))
    image = uiimage_to_png(ui_image)
    with open('text.png', 'wb') as f:
        f.write(image)
    
def clear_cache():
    del objc_util._cached_parse_types_results[b'v88@0:8^v16Q24{MTLRegion}32Q80']

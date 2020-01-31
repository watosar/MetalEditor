from ctypes import *
import objc_util
from objc_util import *
import logger


load_framework('Metal')
CIImage = ObjCClass('CIImage')
NSNull = ObjCClass('NSNull')
CIContext = ObjCClass('CIContext')

CGColorSpaceCreateDeviceRGB = c.CGColorSpaceCreateDeviceRGB
CGColorSpaceCreateDeviceRGB.restype = c_void_p

CGColorSpaceRelease = c.CGColorSpaceRelease
CGColorSpaceRelease.argtypes = [c_void_p]

CGDataProviderCreateWithData = c.CGDataProviderCreateWithData
CGDataProviderCreateWithData.restype = c_void_p

CGImageCreate = c.CGImageCreate
CGImageCreate.restype = c_void_p
CGImageCreate.argtypes = [c_size_t, c_size_t, c_size_t, c_size_t, c_size_t, c_void_p, c_uint32, c_void_p, c_void_p, c_bool, c_int32]

UIImagePNGRepresentation = c.UIImagePNGRepresentation
UIImagePNGRepresentation.restype = c_void_p
UIImagePNGRepresentation.argtypes = [c_void_p]

def CGAffineTransformInitScaleX_Y_translatedbyX_Y_(sx, sy, tx, ty):
    a, d = sx, sy
    b = c = 0
    return (a, b, c, d, tx, ty)

@on_main_thread
def save(mtkview):
    mtkview.framebufferOnly = False
    texture = mtkview.currentDrawable().texture()
    colorSpace = CGColorSpaceCreateDeviceRGB()
    ci_image = CIImage.imageWithMTLTexture_options_(texture, ns(
        {
            'CIImageColorSpace': c_void_p(colorSpace), 
            #'CIImageNearestSampling': 1,
            #'tile_size': [texture.width()/2, texture.height()/2]
        }
    ))
    ci_image = ci_image.imageByApplyingTransform_(CGAffineTransformInitScaleX_Y_translatedbyX_Y_(1, -1, 0, texture.height()))
    ui_image = UIImage.imageWithCIImage_(ci_image)
    resp =  ObjCInstance(UIImagePNGRepresentation(ui_image)).writeToFile_atomically_('./image.png', False)
    CGColorSpaceRelease(colorSpace)
    return resp


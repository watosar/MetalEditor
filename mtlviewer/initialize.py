from .mtlview import MtlView
from .shadercontrollerview import ShaderControllerView

def ready(path):
    mtl_view = MtlView(frame=(0,0,414,414), background_color=(0,.3,0,1))
    controller_view = ShaderControllerView(shaderview=mtl_view, shaderpath=path)
    return mtl_view, controller_view


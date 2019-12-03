from objc_util import *
import os
from ctypes import *
import sys
import time
from pathlib import Path
import math
load_framework('Metal')

MTLCompileOptions, MTLRenderPipelineDescriptor, MTLRenderPipelineReflection = map(ObjCClass,('MTLCompileOptions','MTLRenderPipelineDescriptor', 'MTLRenderPipelineReflection'))



pipeline_state = None
command_queue = None
viewport_size = [1080.0,1080.0]

def get_shader_source(sh_path = Path(__file__).parent/'shader.metal.js'):
    sh_path = Path(sh_path)
    return sh_path.read_text('utf-8')
    

def PyRenderer_mtkView_drawableSizeWillChange_(_self, _cmd, _view, _size):
    '''
    I cannot find the way to get _size arg as CGSize struct
    '''
    global viewport_size
    #print('size change')
    #size = ...
    #viewport_size[:] = size.height, size.width
PyRenderer_mtkView_drawableSizeWillChange_.argtypes = [c_void_p, CGSize]



def PyRenderer_drawInMTKView_(_self, _cmd, _view):
    self = ObjCInstance(_self)
    view = ObjCInstance(_view)
    #view.setClearColor_((1.0,0.0,0.0,1.0))
    command_buffer = command_queue.commandBuffer()
    command_buffer.label = 'MyCommand'
    
    renderpass_descriptor = view.currentRenderPassDescriptor()
    
    if renderpass_descriptor != None:
        
        render_encoder = command_buffer.renderCommandEncoderWithDescriptor_(renderpass_descriptor)
        
        render_encoder.label = "MyRenderEncoder"
    
        view_port = (0.0, 0.0, viewport_size[0], viewport_size[1], 0.0, 1.0)
        #render_encoder.setViewport_(view_port) 
        # TODO : research this func is needed or not
        
        render_encoder.setRenderPipelineState_(pipeline_state)
        
        for index, (arg, c_type) in enumerate(self.py_shader_config['flagment']['args']):
            if callable(arg): arg = arg()
            arg = c_type(arg)
            render_encoder.setFragmentBytes_length_atIndex_(
                byref(arg),
                sizeof(arg),
                index
            )
        
        render_encoder.drawPrimitives_vertexStart_vertexCount_(
            self.py_shader_config['vertex']['PrimitiveType'], #MTLPrimitiveTypeTriangle,
            0, 
            self.py_shader_config['vertex']['count'],
        )
        
        render_encoder.endEncoding()
        command_buffer.presentDrawable_(view.currentDrawable())
        
    command_buffer.commit()


PyRenderer = create_objc_class( 
    'PyRenderer',
    superclass = NSObject,
    methods=[
        PyRenderer_mtkView_drawableSizeWillChange_,
        PyRenderer_drawInMTKView_
    ],
    classmethods=[],
    protocols = ['MTKViewDelegate']
)


def init(view, sh_path):
    global pipeline_state, command_queue
    device = view.device()
    _error  = c_void_p()
    
    default_library = device.newLibraryWithSource_options_error_(get_shader_source(sh_path), MTLCompileOptions.new(), _error)
    
    if _error.value:
        error = ObjCInstance(_error)
        print(error)
        return 
    
    vertex_function = default_library.newFunctionWithName_("vertexShader")
    fragment_function = default_library.newFunctionWithName_("fragmentShader")
    
    pipeline_state_descriptor = MTLRenderPipelineDescriptor.alloc().init()
    pipeline_state_descriptor.label = "Simple Pipeline"
    pipeline_state_descriptor.vertexFunction = vertex_function
    pipeline_state_descriptor.fragmentFunction = fragment_function
    
    pipeline_state_descriptor.colorAttachments().objectAtIndexedSubscript(0).pixelFormat = view.colorPixelFormat()
    
    _error = c_void_p()
    _reflection = c_void_p() # MTLRenderPipelineReflection
    pipeline_state = device.newRenderPipelineStateWithDescriptor_options_reflection_error_(
        pipeline_state_descriptor,
        3, # MTLPipelineOptionArgumentInfo+MTLPipelineOptionBufferTypeInfo
        _reflection,
        _error
    )
    
    if not pipeline_state:
        print(pipeline_state_descriptor_p)
        print("Failed to created pipeline state,",)
        error = ObjCInstance(_error)
        print(error)
        return 
        
    reflection = ObjCInstance(_reflection)
    print(pipeline_state, reflection) 
    command_queue = device.newCommandQueue()
    
    renderer = PyRenderer.new()
    renderer.py_shader_config = {
        'vertex': {'count': 3, 'PrimitiveType': 4},
        'flagment': {'args': [((lambda *,s_time=time.time():time.time() - s_time) , c_float)]}
    }
    return renderer


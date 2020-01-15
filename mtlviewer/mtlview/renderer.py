from objc_util import *
import os
from ctypes import *
import sys
import time
from pathlib import Path
import math
load_framework('Metal')

MTLCompileOptions, MTLRenderPipelineDescriptor, MTLRenderPipelineReflection = map(ObjCClass,('MTLCompileOptions','MTLRenderPipelineDescriptor', 'MTLRenderPipelineReflection'))

c_float_a2 = c_float * 2

pipeline_state = None
command_queue = None
viewport_size = [0.0,0.0]
resolution = c_float_a2(0 ,0)

py_shader_config = {
    'vertex': {
        'count': 3,
        'PrimitiveType': 4 # MTLPrimitiveTypeTriangle
    },
    'flagment': {
        'args': [
            (
                # resolution
                resolution,
                None
            ),
            (
                # time
                (lambda *,s_time=time.time():time.time()-s_time),
                c_float
            ),
        ],
    }
}

def get_shader_source(sh_path = Path(__file__).parent/'shader.metal.js'):
    sh_path = Path(sh_path)
    #print(sh_path)
    return sh_path.read_text('utf-8')
    

def PyRenderer_mtkView_drawableSizeWillChange_(_self, _cmd, view_p, size):
    global viewport_size
    #print('size change', size)
    viewport_size[:] = resolution[:] = size.height, size.width
    #print(viewport_size)
PyRenderer_mtkView_drawableSizeWillChange_.encoding = 'v@:@{CGSize}'
# special thanks for JonB 
# https://forum.omz-software.com/topic/4968/how-can-i-use-return-in-my-objc-class/2


def PyRenderer_drawInMTKView_(_self, _cmd, view_p):
    self = ObjCInstance(_self)
    view = ObjCInstance(view_p)
    #view.setClearColor_((1.0,0.0,0.0,1.0))
    command_buffer = command_queue.commandBuffer()
    command_buffer.label = 'MyCommand'
    
    renderpass_descriptor = view.currentRenderPassDescriptor()
    
    if renderpass_descriptor != None:       
        render_encoder = command_buffer.renderCommandEncoderWithDescriptor_(renderpass_descriptor)
        render_encoder.label = "MyRenderEncoder"
        view_port = (0.0, 0.0, *viewport_size, 0.0, 1.0)
        render_encoder.setViewport_(view_port) 
        # TODO : research whether this func is needed
        
        render_encoder.setRenderPipelineState_(pipeline_state)
        #print(py_shader_config)
        flagment_config = py_shader_config.get('flagment')
        if flagment_config:
            for index, (arg, c_type) in enumerate(flagment_config['args']):
                if callable(arg): 
                    arg = arg()
                if c_type: 
                    arg = c_type(arg)
                render_encoder.setFragmentBytes_length_atIndex_(
                    byref(arg),
                    sizeof(arg),
                    index
                )
        
        vertex_config = py_shader_config.get('vertex')
        if vertex_config:
            render_encoder.drawPrimitives_vertexStart_vertexCount_(
                vertex_config['PrimitiveType'],
                0, 
                vertex_config['count'],
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
        sys.stderr.write(str(error)+'\n')
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
        #print(pipeline_state_descriptor_p)
        #print("Failed to created pipeline state,")
        error = ObjCInstance(_error)
        sys.stderr.write(str(error))
        return 
        
    reflection = ObjCInstance(_reflection)
    #print(pipeline_state, reflection) 
    command_queue = device.newCommandQueue()
    
    renderer = PyRenderer.new()
    return renderer, py_shader_config


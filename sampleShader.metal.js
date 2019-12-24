/*
# set some configs
[Editor]
    timer_limit = 20
    fps = 30

[Vertex]
    count = 3
    type = 4
*/


#include <metal_stdlib>
#include <simd/simd.h>

using namespace metal;

typedef struct{
    float4 position [[position]];
    float4 color;
} RasterizerData;


vertex RasterizerData vertexShader(
    uint vertexID [[vertex_id]]
){

    RasterizerData out;
    
    out.position = float4(sin(2*M_PI_F/3.0*vertexID), cos(2*M_PI_F/3.0*vertexID)-0.25, 0.0, 1.0);
    
    if (vertexID == 0){
        out.color = float4(1.0,0.5,0.0,1.0);
    }
    else if (vertexID == 1){
        out.color = float4(0.0,1.0,0.5,1.0);
    }
    else if (vertexID == 2){
        out.color = float4(0.5,0.0,1.0,1.0);
    }
    
    return out;
    
}


fragment float4 fragmentShader(
    RasterizerData in [[stage_in]],
    constant float &time [[buffer(0)]]
){
    
    in.color.z += sin(time);
    return in.color;
    
}

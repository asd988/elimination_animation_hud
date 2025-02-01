#version 150

#moj_import <fog.glsl>

uniform sampler2D Sampler0;

uniform vec4 ColorModulator;
uniform float FogStart;
uniform float FogEnd;
uniform vec4 FogColor;

in float vertexDistance;
in vec4 vertexColor;
in vec2 texCoord0;

in vec4 textColor;
flat in int type;

out vec4 fragColor;

ivec4 nearest(vec4 v) {
    return ivec4(v*255.0 + 0.5);
}

void main() {
    if (type == -1) {
        discard;
    }

    if (type == 1) {
        fragColor = texture(Sampler0, texCoord0);
        if (fragColor.a < 0.1) {
            discard;
        }

        return;
    }

    // vanilla stuff
    vec4 color = texture(Sampler0, texCoord0) * vertexColor * ColorModulator;
    if (color.a < 0.1) {
        discard;
    }
    fragColor = linear_fog(color, vertexDistance, FogStart, FogEnd, FogColor);
}

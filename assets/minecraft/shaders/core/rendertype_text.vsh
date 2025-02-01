#version 150

#moj_import <fog.glsl>

in vec3 Position;
in vec4 Color;
in vec2 UV0;
in ivec2 UV2;

uniform sampler2D Sampler0;
uniform sampler2D Sampler2;

uniform mat4 ModelViewMat;
uniform mat4 ProjMat;
uniform int FogShape;

uniform float GameTime; // have to be included in the json

out float vertexDistance;
out vec4 vertexColor;
out vec2 texCoord0;

flat out int type;

const vec2 corners[4] = vec2[](
    vec2(0.0, 1.0),
    vec2(0.0, 0.0),
    vec2(1.0, 0.0),
    vec2(1.0, 1.0)
);

// gets the nearest integer color, good for wider support
ivec4 nearest(vec4 v) {
    return ivec4(v*255.0 + 0.5);
}

vec2 calcGuiPixel(mat4 ProjMat) {
    return abs(vec2(ProjMat[0][0], ProjMat[1][1]));
}

void main() {
    // vanilla stuff
    gl_Position = ProjMat * ModelViewMat * vec4(Position, 1.0);

    vertexDistance = fog_distance(Position, FogShape);
    vertexColor = Color * texelFetch(Sampler2, UV2 / 16, 0);
    texCoord0 = UV0;


    type = 0;
    
    // Animation branch
    ivec4 iTextureColor = nearest(texture(Sampler0, vec2(0, 0)));
    if (iTextureColor == ivec4(132, 148, 45, 153)) { // check against the identifer color
        // Remove shadow
        if (Position.z == 2200.0) {
            type = -1;
            return;
        }
        type = 1;
        
        // decode the encoding, for more info check how it's generated in script.py
        vec4 meta = texelFetch(Sampler0, ivec2(1, 0), 0);
        int frames = int(meta.r * 255.0);
        vec2 spriteSize = meta.gb;
        int frameRateEnum = int(meta.a * 255.0);
        float frameRate = frameRateEnum == 1 ? 14.0 : 56.0 / 3.0;

        ivec4 iColor = nearest(Color);
        float tick = GameTime * 24000;
        
        float exTick = iColor.r | (iColor.g << 8); // convert color back
        exTick += 0.5;

        int frame = int((tick - exTick) / 20.0 * frameRate);

        if (frame < 0) {
            frame = 0;
        } else if (frame >= frames) {
            frame = frames - 1;
        }

        // get the current frame's data
        vec4 frameData0 = texelFetch(Sampler0, ivec2(2 + frame * 2, 0), 0);
        vec4 frameData1 = texelFetch(Sampler0, ivec2(2 + frame * 2 + 1, 0), 0);
        vec2 pos = frameData0.rg;
        vec2 size = frameData0.ba;
        vec2 offset = frameData1.rg;
        bool rotated = frameData1.b > 0.5;

        vec2 pixel = calcGuiPixel(ProjMat);
        vec2 corner = corners[gl_VertexID % 4];
        vec2 imgCorner = corners[(gl_VertexID + int(rotated)) % 4];
        imgCorner.y = 1.0 - imgCorner.y;
        corner -= vec2(0.0, 1.0);

        texCoord0 = (pos + imgCorner * (rotated ? size.yx : size)) * 255.0 / 256.0;

        const float scale = 255 * 2;
        size *= scale; offset *= scale; spriteSize *= scale;
        
        gl_Position.xy += vec2(-0.5, 1) * vec2(spriteSize.x, 80*2) * pixel;
        gl_Position.y -= 32 * pixel.y;
    

        gl_Position.xy += (offset * vec2(1, -1) + corner * size) * pixel;
    }
}

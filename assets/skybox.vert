#version 410 core

layout (location = 2) in vec3 pos;

uniform mat4 MVP;

out vec3 uvw;

void main()
{
    vec4 transformed_pos = MVP * vec4(pos, 1.0);
    gl_Position = transformed_pos.xyww;
    uvw = pos;
} 
#version 410 core

in vec3 uvw;

out vec4 color;

uniform samplerCube cube_tex;

void main()
{
	color = texture(cube_tex, uvw);
} 
#version 410 core

layout (location = 0) in vec2 vert_uv;
layout (location = 1) in vec3 vert_norm;
layout (location = 2) in vec3 vert_pos;

uniform mat4 MVP;

out vec2 uv;

void	main()
{
	vec4 position = MVP * vec4(vert_pos, 1.0);
	gl_Position = position;
	uv = vert_uv;
}
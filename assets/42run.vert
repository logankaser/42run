#version 410 core

layout(location = 0) in vec2 vert_uv;
layout(location = 1) in vec3 vert_norm;
layout(location = 2) in vec3 vert_pos;

uniform mat4 MVP;
uniform mat4 MV;
uniform mat4 V;
uniform mat4 M;

out vec2 uv;
out vec3 norm;
out	vec3 camera_dir;

void	main()
{
	gl_Position = MVP * vec4(vert_pos, 1.0);
	uv = vert_uv;
	norm = vec3(MV * vec4(vert_norm, 0.0));
	camera_dir = vec3(0.0, 0.0, 0.0) - (MV * vec4(vert_pos, 1.0)).xyz;
}
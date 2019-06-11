#version 410 core

precision mediump float;

in vec2 uv;
in vec3 norm;
in vec3 camera_dir;

const vec3 light = normalize(vec3(0.0, 6.0, 10.0));

out vec4 color;

uniform sampler2D tex;

void	main()
{
	vec3 c = texture(tex, uv).rgb;
	float a = texture(tex, uv).a;

	vec3 n = normalize(norm);
	float cos_theta = dot(n, light);

	vec3 E = normalize(camera_dir);
	vec3 R = reflect(-light, n);

	float cos_alpha = clamp(dot(E, R), 0.00001, 1.0);

	c *= max(cos_theta, 0.2) + vec3(pow(cos_alpha, 9.0));
	color = vec4(c, a);
}
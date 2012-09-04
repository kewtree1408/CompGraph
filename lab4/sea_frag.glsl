
//~ освещение Фонга с текструированием
varying vec3 n;
varying vec3 l1;
varying vec3 v1;

uniform sampler2D decalMap;

vec4 setLightTexFong() {
	const vec4 specColor = vec4( 0.7, 0.7, 0.0, 1.0);
	const float specPower = 20.0;
	
	vec4 diffColor = texture2D(decalMap, gl_TexCoord[0].xy);
	vec3 n2 = normalize(n);
	vec3 l2 = normalize(l1);
	vec3 v2 = normalize(v1);
	vec3 r = reflect(-v2,n2);
	vec4 diff = diffColor * max( dot(n2,l2), 0.0);
	vec4 spec = specColor * pow( max(dot(l2,r),0.0), specPower);
	return diff + spec;
}

//~ blinn
varying vec3 lb;
varying vec3 hb;
varying vec3 vb;


vec4 setLightBlinn() {
	const vec4 diffColor = vec4 ( 0.7, 0.3, 0.5, 1.0);
	const vec4 specColor = vec4 ( 0.7, 0.7, 0.0, 1.0);
	const float specPower = 20.0;
	
	vec3 n2 = normalize(n);
	vec3 l2 = normalize(lb);
	vec3 h2 = normalize(hb);
	vec4 diff = diffColor * max ( dot(n2,l2), 0.0);
	vec4 spec = specColor * pow ( max (dot(n2,h2),0.0),specPower);
	
	return diff+spec;
}

void main() {
	vec4 color = texture2D(decalMap,gl_TexCoord[0].st);
	gl_FragColor = (setLightTexFong()+setLightBlinn())*color;
}

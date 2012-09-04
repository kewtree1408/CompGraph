
//~ освещение Фонга с текструированием
varying vec3 n; 
varying vec3 l1;
varying vec3 v1;

uniform vec4 lightPos;
uniform vec4 eyePos;

void setLightTexFong(){
	vec3 p = vec3( gl_ModelViewMatrix * gl_Vertex);
	
	l1 = normalize( vec3(lightPos) - p);
	v1 = normalize( vec3(eyePos) - p);
	n = normalize( gl_NormalMatrix * gl_Normal);
}

varying vec3 lb;
varying vec3 hb;
varying vec3 vb;

uniform vec4 lightPosb;
uniform vec4 eyePosb;

void setLightBlinn() {
	vec3 p = vec3 ( gl_ModelViewMatrix * gl_Vertex);
	lb = normalize ( vec3(lightPosb) - p);
	vb = normalize ( vec3(eyePosb) - p);
	hb = normalize ( lb+vb);
	n = normalize ( gl_NormalMatrix * gl_Normal);
	
}

void main() {
	setLightTexFong();
	setLightBlinn();
	gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
	gl_TexCoord[0] = gl_MultiTexCoord0;
}

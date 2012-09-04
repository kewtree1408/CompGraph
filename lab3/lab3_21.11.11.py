#!/usr/bin/python
# -*- coding: utf-8 -*-

import OpenGL
import OpenGL.GL
import OpenGL.GLU
import OpenGL.GLUT
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from numpy import *
from math import *

looping=True
yaw = 0
pitch = 0
roll = 0
initLight = array([-1,1,1])
initEye = array([-1,1,1])
size = 1
def rotateX(a):
	s = sin(a)
	c = cos(a)
	return array([[1, 0, 0],
				  [0, c, -s],
				  [0, s, c]] )
	
def rotateY(a):
	s = sin(a)
	c = cos(a)
	return array([[c, 0, s],
				  [0, 1, 0],
				  [-s, 0, c]] )
	
def rotateZ(a):
	s = sin(a)
	c = cos(a)
	return array([[c , -s, 0],
				  [s, c , 0],
				  [0, 0, 1 ]] )

def formulConus(a,b):
    return array([sin(a)*(1-b)/2,cos(a)*sin(1-b)/2,-b])
    
def MakeConus():
    def frange(start,end,step): 
	return map(lambda x: x*step, range(int(start*1.0/step),int(end*1.0/step)))

    points = []
    pi = atan(1)*4
    st = 0.5
    #~ st = 0.1
    st = pi / int(pi / st)

    for a in frange(0, 2*pi, st):
	    for b in frange(-1, 0.98, st):
		    ltmp = [formulTorus(v,u) 
				    for v,u in 
				    ((a,b), (a+st,b),
				    (a+st,b), (a+st,b+st),
				    (a+st, b+st), (a+st,b),
				    (a+st,b), (a,b))
			    ]
		    points.extend(ltmp)
					    
    return points
    
def formulTorus(v, u, D = 2.0, A = 1.0):
	return array([(D+A*cos(v))*cos(u), (D+A*cos(v))*sin(u), A*sin(v)])

def MakeTorus():	
    def frange(start,end,step): 
	return map(lambda x: x*step, range(int(start*1.0/step),int(end*1.0/step)))

    points = []
    pi = atan(1)*4
    st = 0.5
    #~ st = 0.1
    st = pi / int(pi / st)
    
    for a in frange(-pi-st, pi+st, st):
	    for b in frange(-pi-st, pi+st, st):
		    ltmp = [formulTorus(v,u) 
				    for v,u in 
				    ((a,b), (a+st,b),
				    (a+st,b), (a+st,b+st),
				    (a+st, b+st), (a+st,b),
				    (a+st,b), (a,b))
			    ]
		    points.extend(ltmp)
					    
    return points

def formulCircle(a,b):
    return array([sin(a)*cos(b), cos(a)*cos(b), sin(b)])
    #~ return array([a*cos(b),a*sin(b),1])

def MakeCircle():
    def frange(start,end,step): 
	return map(lambda x: x*step, range(int(start*1.0/step),int(end*1.0/step)))

    points = []
    pi = atan(1)*4
    st = 0.4
    st = pi / int(pi / st)
    #~ st = 2*pi/200.0
    #~ st = atan(1)*0.4
    
    for a in frange(0, 2*pi, st):
	for b in frange(-pi/2, pi/2, st):
	    ltmp = [formulCircle(v,u) 
		    for v,u in ((a,b), (a+st,b), (a+st,b+st), (a, b+st))
		    #~ for v,u in ((a,b), (a+st,b),
				#~ (a+st,b), (a+st,b+st),
				#~ (a+st, b+st), (a+st,b),
				#~ (a+st,b), (a,b))
		    ]
	    points.extend(ltmp)
					
    return points

def normalize(F):
    return F*1.0/sqrt(F[0]**2+F[1]**2+F[2]**2)


angleRotate = 0.1
def kbd(k,x,y):
    global looping, angleRotate
    global yaw, pitch, roll
    if k == 'q':
        looping=False
    if k == 'w':
        yaw += angleRotate
    if k == 's':
        yaw -= angleRotate
    if k == 'a':
        pitch += angleRotate
    if k == 'd':
        pitch -= angleRotate
    if k == 'z':
        roll += angleRotate
    if k == 'c':
        roll -= angleRotate
    #~ print(yaw,pitch,roll)


def Rotate(figure):
    global yaw, pitch, roll
    M = eye(3,3)
    global size
    #~ создали матрицу поворота
    M = dot(M,rotateX(pitch))
    M = dot(M,rotateY(yaw))
    M = dot(M,rotateZ(roll))
    figure = [size*dot(M,v) for v in figure]
    return figure
    
def SetLightWard(n,l,v,k=10.0,
		diffColor=array([0.5, 0.0, 0.0, 1.0]),
		specColor=array([0.7, 0.7, 0.0, 1.0])):
    
    n = normalize(n) #normalize
    l = normalize(l)
    h = l + v 
    h = normalize(h)
    hn = dot(h,n)
    hn2 = hn**2
    
    diff = diffColor * max(dot(n, l),0.0)
    spec = specColor * exp(-k*(1.0 - hn2)/hn2)
    
    resultColor = diff+spec
    return resultColor[0], resultColor[1], resultColor[2], resultColor[3]


def DrawFigure(figure):
    figure = Rotate(figure)
    lenFigure = len(figure)
        
    for i in xrange(0,len(figure),4):
	v1, v2, v3, v4 = figure[i], figure[i+1], figure[i+2], figure[i+3]
	norm = cross(v1-(v2+v3)*0.5, v1-(v3+v4)*0.5)
	avg = (v1+v2+v3+v4)/4.0
	if norm[2]>0.0:
	    vectLight = initLight - avg
	    vectEye = initEye - avg
	    c1,c2,c3,c4=SetLightWard(norm, vectLight, vectEye)
	    glColor4f(c1,c2,c3,c4)
	    
	    glBegin(GL_POLYGON)
	    glVertex3f(v1[0], v1[1], v1[2])
	    glVertex3f(v2[0], v2[1], v2[2])
	    glVertex3f(v3[0], v3[1], v3[2])
	    glVertex3f(v4[0], v4[1], v4[2])
	    glEnd()
		

def DrawFiguretmp(figure):
    figure = Rotate(figure)
    lenFigure = len(figure)
    
    for i in xrange(0,lenFigure,4):
	#~ glBegin(GL_POLYGON)
	#~ нашли вектор нормали
	#~ if (i%3==0 and i<lenFigure-3): 
	norm = cross((figure[i+1]-figure[i+2]),(figure[i+2]-figure[i+3]))
	#~ среднее значение полигона
	avg = (figure[i]+figure[i+1]+figure[i+2]+figure[i+3])/4.0
	vectLight = initLight-avg
	vectEye = initEye-avg
	if norm[2]>0.0:
	    c1,c2,c3,c4=SetLightWard(norm, vectLight, vectEye)
	    glColor4f(c1,c2,c3,c4)
	#~ glColor4f(0,0,0,0)
	#~ glBegin(GL_POLYGON)
	#~ glVertex3f(v[0],v[1],v[2])
	glBegin(GL_QUADS)
	glVertex3f(figure[i][0],figure[i][1],figure[i][2])
	glVertex3f(figure[i+2][0],figure[i+2][1],figure[i+2][2])
	glVertex3f(figure[i+3][0],figure[i+3][1],figure[i+3][2])
	glVertex3f(figure[i+1][0],figure[i+1][1],figure[i+1][2])
	glEnd()	

    

def display():
    #~ glClearColor(0.5,0.8,0.9,1.0)
    glClearColor(0.,0.,0.2,1.0)    
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(90,1.0*glutGet(GLUT_WINDOW_WIDTH)/glutGet(GLUT_WINDOW_HEIGHT),0.1,100.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    #~ glEnable(GL_DEPTH_TEST)
    #~ glEnable(GL_CULL_FACE)
    glTranslatef(0,0,-3)
    #~ glScale(0.75,0.75,0.75)
    
    torr = MakeTorus()
    circle = MakeCircle()
    conus = MakeConus()
    DrawFigure(conus)
    #~ DrawFigure(torr)
    glutSwapBuffers()

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE|GLUT_RGBA|GLUT_DEPTH)
    glutCreateWindow('light_ward')
    glutDisplayFunc(display)
    glutKeyboardFunc(kbd)
    while(looping):
        glutMainLoopEvent()
        glutPostRedisplay()
    pass


if __name__ == '__main__':
	main()

#!/usr/bin/python
# -*- coding: utf-8 -*-

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from math import *
import Image


#~ Stolen from http://pyopengl.sourceforge.net/context/nehe6.html
def loadImage( imageName ):
    """Load an image file as a 2D texture using PIL

    This method combines all of the functionality required to
    load the image with PIL, convert it to a format compatible
    with PyOpenGL, generate the texture ID, and store the image
    data under that texture ID.

    Note: only the ID is returned, no reference to the image object
    or the string data is stored in user space, the data is only
    present within the OpenGL engine after this call exits.
    """
    im = Image.open(imageName)
    try:
            # get image meta-data (dimensions) and data
            ix, iy, image = im.size[0], im.size[1], im.tostring("raw", "RGBA", 0, -1)
    except SystemError:
            # has no alpha channel, synthesize one, see the
            # texture module for more realistic handling
            ix, iy, image = im.size[0], im.size[1], im.tostring("raw", "RGBX", 0, -1)
    # generate a texture ID
    ID = glGenTextures(1)
    # make it current
    glBindTexture(GL_TEXTURE_2D, ID)
    glPixelStorei(GL_UNPACK_ALIGNMENT,1)
    # copy the texture into the current texture ID
    #glTexImage2D(GL_TEXTURE_2D, 0, 4, ix, iy, 0, GL_RGBA, GL_UNSIGNED_BYTE, image)
    gluBuild2DMipmaps(GL_TEXTURE_2D, GL_RGBA, ix, iy, GL_RGBA, GL_UNSIGNED_BYTE, image)
    
    # return the ID for use
    return ID


looping = True
eltime = 0
keys = {}
prevx = prevy = 0
points = []	

class Camera(object):
	def __init__(self):
		self.x = 5
		self.y = 2
		self.z = 1.5
		self.vx = self.vy = self.vz = .0
		self.yaw = 190.0
		self.pitch = -0.5
		self.goA = self.goD = self.goW = self.goS = False
		
	
	def move(self,dt):
		speed = 0.0000003
		if self.goW:
			self.vx=cos(self.yaw)*cos(self.pitch)
			self.vy=sin(self.yaw)*cos(self.pitch)
			self.vz=sin(self.pitch)

		if self.goS:
			self.vx=-cos(self.yaw)*cos(self.pitch)
			self.vy=-sin(self.yaw)*cos(self.pitch)
			self.vz=-sin(self.pitch)
        
		if self.goA:
			self.vx=-sin(self.yaw)*cos(self.pitch)
			self.vy=cos(self.yaw)*cos(self.pitch)
			
		if self.goD:
			self.vx=sin(self.yaw)*cos(self.pitch)
			self.vy=-cos(self.yaw)*cos(self.pitch)
		
		self.vx*=speed
		self.vy*=speed
		self.vz*=speed
		self.x+=self.vx*dt
		self.y+=self.vy*dt
		self.z+=self.vz*dt
		
		#~ self.z = checkSurface(self.x,self.y,self.z)
		#~ self.x,self.y,self.z = checkBorder(self.x,self.y,self.z)
		
		self.vx=self.vy=self.vz=.0

camera = Camera()

#~ not used
def click(button, state, x, y):
    if state == GLUT_DOWN and button == GLUT_LEFT_BUTTON:
	print (x,y)
	points.append((x/100.0,y/100.0))
	#~ points.append((x,y))

def mouse(x,y):
    global prevx,prevy
    dx=prevx-x
    dy=prevy-y
    camera.yaw+=dx*0.01
    camera.pitch+=dy*0.01
    pi2 = atan(1)*2
    if camera.pitch>pi2: camera.pitch=pi2
    if camera.pitch<-pi2: camera.pitch=-pi2
    prevx=x
    prevy=y
    

def kbd_down(k,x,y):
    if k=='w':
        camera.goW=True
    if k=='s':
        camera.goS=True
    if k=='a':
        camera.goA=True
    if k=='d':
        camera.goD=True
    
    global looping
    if k=='q':
        looping=False
    keys[k]=True

def kbd_up(k,x,y):
    if k=='w':
        camera.goW=False
    if k=='s':
        camera.goS=False
    if k=='a':
        camera.goA=False
    if k=='d':
        camera.goD=False
    
    keys[k]=False

def Bspline(coords):
    N = 30
    bspline = []
    for i in range(0,len(coords)-3,1):
	xA, yA = coords[i][0], coords[i][1]
	xB, yB = coords[i+1][0], coords[i+1][1]
	xC, yC = coords[i+2][0], coords[i+2][1]
	xD, yD = coords[i+3][0], coords[i+3][1]
	
	a3 = (-xA + 3 * (xB - xC) + xD) / 6.0
	a2 = (xA - 2 * xB + xC) / 2.0
	a1 = (xC - xA) / 2.0
	a0 = (xA + 4 * xB + xC) / 6.0
	
	b3 = (-yA + 3 * (yB - yC) + yD) / 6.0
	b2 = (yA - 2 * yB + yC) / 2.0
	b1 = (yC - yA) / 2.0
	b0 = (yA + 4 * yB + yC) / 6.0
	
	for i in range(N):
	    t = i*1.0/N
	    X = (((a3 * t + a2) * t + a1) * t + a0)
	    Y = (((b3 * t + b2) * t + b1) * t + b0)
	    Z = sin(X)
	    bspline.append((X,Y,Z))

    return bspline
    
def AutogenFile(filename):
    """Генерация опорных точек в файл"""
    inits = [(10*sin(t*5),10*cos(t*10)) for t in xrange(0,100)]
    
    f = open(filename,'w+')
    #~ write first coords
    for x,y in inits:
	f.write(repr(x))
	f.write(' ')
	f.write(repr(y))
	f.write('\n') 
    f.write('---\n')
    
    #~ write second coords
    for x,y in inits:
	f.write(repr(x+10.0))
	f.write(' ')
	f.write(repr(y+5.0))
	f.write('\n') 
    

def GetFromFile(filename):
    """ Считывание точек для 2х Сплайнов из файла"""
    coord1 = []
    coord2 = []
    addBs2fl = False
    for s in open(filename).readlines():
	data = s.split()
	if data == ['---']:
	     addBs2fl = True
	elif len(data)==2 and not addBs2fl:
	    x,y = (float(data[0]),float(data[1]))
	    coord1.append((x,y))
	elif len(data)==2 and addBs2fl:
	    x,y = (float(data[0]),float(data[1]))
	    coord2.append((x,y))
	else:
	    print("Incorrect file-map")
	    exit(1)
    
    assert(len(coord1)==len(coord2))
    assert(len(coord1)>=4 and len(coord2)>=4)
    #~ print(coord1,coord2)
    
    Bs1,Bs2 = Bspline(coord1), Bspline(coord2)
    #~ nulst = [(0,0,0) for i in xrange(4)]
    return Bs1,Bs2
    
def Draw(coords):
    glBegin(GL_LINE_STRIP)
    for x,y,z in coords:
	glVertex3d(x,y,z)
    glEnd()

idSurface=0    
def DrawSurface():
    """ Построение линейчатой поверхности по 2м кривым"""
    
    global idSurface
    if idSurface:
        #~ рисуем видимую часть
        glCallList(idSurface)
    else:
        #~ генерируем набор дисплейных списков
        idSurface=glGenLists(1)
        glNewList(idSurface,GL_COMPILE_AND_EXECUTE)
	
	
	B1,B2 = GetFromFile("explode.map")
	n = len(B1)
	glBegin(GL_QUADS)
	for i in xrange(1,n):
	    x1,y1,z1 = B1[i]
	    x2,y2,z2 = B2[i]
	    x3,y3,z3 = B2[i-1]
	    x4,y4,z4 = B1[i-1]
	    
	    #~ glNormal3fv(CN(x1,y1))
	    glTexCoord2f(x1,y1)
	    glVertex3fv(B1[i])
	    
	    #~ glNormal3fv(CN(x2,y2))
	    glTexCoord2f(x2,y2)
	    glVertex3fv(B2[i])
	    
	    #~ glNormal3fv(CN(x3,y3))
	    glTexCoord2f(x3,y3)
	    glVertex3fv(B2[i-1])
	    
	    #~ glNormal3fv(CN(x4,y4))
	    glTexCoord2f(x4,y4)
	    glVertex3fv(B1[i-1])
	    
	glEnd()
	glEndList()
    
inited=False
tex1=0
def initOnce():
    global inited
    if inited: return
    inited=True
    global tex1
    tex1=loadImage("sun.png")
    #~ tex1=loadImage("snake.png")
    #~ AutogenFile("explode.map")

def display():
    initOnce()
    global eltime
    curtime=glutGet(GLUT_ELAPSED_TIME)
    #~ разница подгрузки
    dt=curtime-eltime
    curtime=eltime
    
    camera.move(dt)
    
    glClearColor(0.3,0.3,0.7,1.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(90,1.0*glutGet(GLUT_WINDOW_WIDTH)/glutGet(GLUT_WINDOW_HEIGHT),0.1,100.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(camera.x,camera.y,camera.z,
              camera.x+cos(camera.yaw)*cos(camera.pitch),
              camera.y+sin(camera.yaw)*cos(camera.pitch),
              camera.z+sin(camera.pitch),
              0,0,1)

    glEnable(GL_DEPTH_TEST)
    glEnable(GL_CULL_FACE)
    glEnable(GL_NORMALIZE)
    glEnable(GL_TEXTURE_2D)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
    glBindTexture(GL_TEXTURE_2D, tex1)
    
    DrawSurface()
    
    glutSwapBuffers()

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE|GLUT_RGBA|GLUT_DEPTH)
    glutInitWindowSize(800,600)
    glutCreateWindow('B-spline')
    
    glutDisplayFunc(display)
    glutKeyboardFunc(kbd_down)
    glutKeyboardUpFunc(kbd_up)
    glutPassiveMotionFunc(mouse)
    glutMouseFunc(click)
    while(looping):
        glutMainLoopEvent()
        glutPostRedisplay()


if __name__ == "__main__":
	main()

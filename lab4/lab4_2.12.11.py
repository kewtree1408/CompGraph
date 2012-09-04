#!/usr/bin/python
# -*- coding: utf-8 -*-


import OpenGL 
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
# PyOpenGL 3.0.1 introduces this convenience module...
from shaders import *

from math import *
from random import *
import Image


#~ -----------Глобальные переменные-------------
looping = True
#~ истекшее время
eltime = 0
keys = {}
prevx = prevy = 0		
idSurface = 0
textures={}
BORDER = 40
alphaSun = 0
alphaIco = 0
#~ Создаем указатель на квадратичный объект ( НОВОЕ )
quadratic=0
sprites=[]

stateBorder = False
nloX = 0
nloY = 0

program = None

def FSurf(x,y):    
	return cos(0.5*x)+sin(0.7*y)*cos(0.9*y)


def checkSurface(cx,cy,cz):	
    """Если столкнулись с "волнами", то возвращаем значение координаты z,
    иначе оставляем ее как есть"""	
    de = 0.25
    z = cz
    if (cz-FSurf(cx,cy)) < de:
	z = FSurf(cx,cy)+de
    return z

def checkBorder(sx,sy,sz):
    """ Проверка на столкновение с берегом и выхода за границы экрана. 
    Возвращаем "координаты столкновения"."""

    x,y,z = sx,sy,sz
    
    if x>BORDER-3.0:
	    sx = BORDER-3.0
    if y>BORDER:
	    sy = BORDER
    if x<0.5 :
	    sx = 0.5
    if y<0.5 :
	    sy = 0.5
    if z>7.0:
	    sz = 7.0
    if z-3.0 > 0.5:
	    sz -= 0.1
    
    return sx,sy,sz

def checkIco(sx,sy):
    """ Проверка на столкновение с икосаэдром """
    de = 2.0
    if (5.0-sy)<de and sx-5.0<de:
	sy -= de/4
    if (sy-5.0)<de and sx+5.0<de:
	sy += de/4
    return sx,sy

class Camera(object):
	def __init__(self):
		self.x = BORDER/2+5
		self.y = 2
		self.z = 1.5
		self.vx = self.vy = self.vz = .0
		self.yaw = 190.0
		self.pitch = -0.5
		self.goA = self.goD = self.goW = self.goS = False
	
	
	
	def move(self,dt):
		speed = 0.00003
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
		
		self.z = checkSurface(self.x,self.y,self.z)
		self.x,self.y,self.z = checkBorder(self.x,self.y,self.z)
		self.x,self.y = checkIco(self.x,self.y)
		
		self.vx=self.vy=self.vz=.0

camera = Camera()
		
class Sprite(object):
    def __init__(self):
	self.x = BORDER-1
	self.y = 5.0
	self.z = 1.0
	self.tex = "pic/tree.png"
    
    def draw(self):
	setTexture(self.tex)
    
	glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
	if keys.get('1'):
	  glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
	  glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
	else:
	  glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
	  glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
	glEnable(GL_BLEND)
	glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
	glEnable(GL_ALPHA_TEST)
	glAlphaFunc(GL_GREATER,0.1)
	
	glPushMatrix()
	glTranslatef(self.x,self.y,self.z)
	if self.tex == 'ships/ship2.png':
	    glRotate(180,0,0,1)
	    glNormal3f(0,-1,1)
	else:
	    glNormal3f(0,1,1)
	glRotatef(90+camera.yaw*180/(atan(1)*4),0,0,1)
	glBegin(GL_QUADS)
	
	glColor3f(1,1,1,1)
	
	h=1.
	w=0.5
	
	glTexCoord2f(0,0)
	glVertex3f(-w,0,0)
	
	glTexCoord2f(0,1)
	glVertex3f(-w,0,1)
	
	glTexCoord2f(-1,1)
	glVertex3f(w,0,1)
	
	glTexCoord2f(-1,0)
	glVertex3f(w,0,0)
	glEnd()
	glPopMatrix()
	
	glDisable(GL_BLEND)
    
    def move(self,F):
	global stateBorder, nloX, nloY		
	x, y, z = self.x, self.y, self.z
	
	if (0<x<BORDER-3 and 0<y<BORDER-2):
	    i = random()*0.01
	    #~ print(i)
	    y += i
	    x += F(i)
	    z = FSurf(x,y)-0.2
	    self.x, self.y, self.z = x, y, z
	else:
	    stateBorder = True
	    nloX = self.x
	    nloY = self.y
	    sprites.remove(self)


#~ ----------------------

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

def getTextureId(name):
    if name in textures:
        return textures[name]
    textures[name]=loadImage(name)
    return textures[name]

def setTexture(name):
    i = getTextureId(name)
    glBindTexture(GL_TEXTURE_2D, i)

def sunLight():
    glEnable(GL_LIGHT1)
    #~ желтый блик от солнца
    glLightfv(GL_LIGHT1,GL_SPECULAR,(0,1,0,1))
    glLightfv(GL_LIGHT1,GL_POSITION,(40,1,1,0))
    
    
def setupLight():
    glEnable(GL_LIGHT0)
    
    #~ позиция освещения зависит от солнца
    #~ glLightfv(GL_LIGHT0,GL_POSITION,(0,1,1,0))
    
    #~ рассеянный цвет (голубой)
    glLightfv(GL_LIGHT0,GL_DIFFUSE,(0.2,0.8,0.9,0.7))
    #~ фоновый цвет (голубой)
    glLightfv(GL_LIGHT0,GL_AMBIENT,(.2,.5,.6,1))
    #~ отраженный цвет от объекта (синий)
    glLightfv(GL_LIGHT0,GL_SPECULAR,(0,0,1,0.5))
    

#~ Метод Ньюэлла
#~ считаем нормали к граням
def NormEdge(lst):
    N = len(lst)
    def next(idx):
        return (idx+1)%N
    
    vx = []; vy = []; vz = [];
    #~ разбиваем на список вершин:
    for i in xrange(0,N-2,3):
        vx.append(lst[i])
        vy.append(lst[i+1])
        vz.append(lst[i+2])	
			
    N = N/3		
    mix = [(vy[i]-vy[next(i)])*(vz[i]+vz[next(i)]) for i in xrange(N-1)]
    miy = [(vz[i]-vz[next(i)])*(vx[i]+vx[next(i)]) for i in xrange(N-1)]
    miz = [(vx[i]-vx[next(i)])*(vy[i]+vy[next(i)]) for i in xrange(N-1)]
	
    normVect = [ sum(elem) for elem in (mix,miy,miz) ]
    return normVect
    
#~ нормальный вектор к поверхности
def NormSurface(lst):
    #~ стандартный метод
    def CN(x,y):
	dzdx=FSurf(x+1,y)-FSurf(x,y)
	dzdy=FSurf(x,y+1)-FSurf(x,y)
	(x,y,z)=(-dzdx,-dzdy,1)
	ab=(x*x+y*y+z*z)**0.5
	return (x/ab,y/ab,z/ab)
    
    nlst = []
    for i in xrange(0,len(lst),3):
	nlst.extend(CN(lst[i],lst[i+1]))
    return nlst
    
def TextureSurface(lst):
    return [lst[i] for i in xrange(len(lst)) if (i+3)%3!=0]
    
def drawSurface():
    def frange(start,end,step): 
		return map(lambda x: x*step, range(int(start*1.0/step),int(end*1.0/step)))
    
    glColor4f(0,0,1,1)
    setTexture('pic/sea.png')
    
    glPushMatrix()
    #~ отраженный цвет матриала (голубой)
    glMaterialfv(GL_FRONT,GL_SPECULAR,(0,0.7,0.6,1))
    #~ коэффициент зеркального отражения (максимум зеркального блика)
    glMaterialf(GL_FRONT,GL_SHININESS,128)
    glPopMatrix()
    
    global idSurface
    if idSurface:
        #~ рисуем видимую часть
        glCallList(idSurface)
    else:
        #~ генерируем набор дисплейных списков
        idSurface=glGenLists(1)
        glNewList(idSurface,GL_COMPILE_AND_EXECUTE)
        
        #~ поверхность из частичек квадратиков
        #~ массив вершин
	color1 = [1,0,0,1]
	glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_NORMAL_ARRAY)
	glEnableClientState(GL_TEXTURE_COORD_ARRAY)
        #~ glEnableClientState(GL_COLOR_ARRAY)
	
	vserf = []
        for x in frange(0,BORDER,1.0):
	    for y in frange(0,BORDER,1.0):
		xx=x+1.0
		yy=y+1.0
		    
		vserf.extend([x,y,FSurf(x,y)])
		vserf.extend([xx,y,FSurf(xx,y)])
		vserf.extend([xx,yy,FSurf(xx,yy)])
		vserf.extend([x,yy,FSurf(x,yy)])
		
	nserf = NormSurface(vserf)
	texserf = TextureSurface(vserf)
	
	glVertexPointer(3,GL_FLOAT,0,vserf)
	glNormalPointer(GL_FLOAT,0,nserf)
	glTexCoordPointer(2,GL_FLOAT,0,texserf)
	#~ glColorPointer(4,GL_INT,0,color1)
	glDrawArrays(GL_QUADS,0,4*BORDER*BORDER)
	
        #~ glDisableClientState(GL_COLOR_ARRAY)
        glDisableClientState(GL_TEXTURE_COORD_ARRAY)
	glDisableClientState(GL_NORMAL_ARRAY)
        glDisableClientState(GL_VERTEX_ARRAY)
	
	glEndList()
	
	
#~ рисуем солнце как шар
def drawSun():
    
    global alphaSun
    alphaSun += 0.1
    
    global quadratic
    quadratic = gluNewQuadric() 
    #~ Создаем плавные нормали ( НОВОЕ )
    gluQuadricNormals(quadratic, GLU_SMOOTH) 
    #~ Создаем координаты текстуры ( НОВОЕ )   
    gluQuadricTexture(quadratic, GL_TRUE)
    gluQuadricDrawStyle(quadratic, GLU_FILL);
    
    setTexture('pic/sun.png')
    
    glPushMatrix()
    #~ отраженный цвет матриала (желтый)
    glMaterialfv(GL_FRONT,GL_SPECULAR,(1,1,0,1))
    #~ коэффициент зеркального отражения (максимум зеркального блика)
    glMaterialf(GL_FRONT,GL_SHININESS,128)
    
    glRotate(-alphaSun,1,1,0)
    glTranslate(BORDER,0,BORDER/2)
    gluSphere(quadratic,0.5,16,16)
    
    #~ свет от солнца
    sunLight()
    glPopMatrix()
    
#~ рисуем один раз
idCube = 0
def drawCube():    
    global idCube
    if idCube:
        #~ рисуем видимую часть
        glCallList(idCube)
    else:
        #~ генерируем набор дисплейных списков
        idCube=glGenLists(1)
        glNewList(idCube,GL_COMPILE_AND_EXECUTE)
        
        #~ массив вершин
	
	vedges = [1,1,1,  -1,1,1,  -1,-1,1,  1,-1,1,        
                      1,1,1,  1,-1,1,  1,-1,-1,  1,1,-1,        
                      1,1,1,  1,1,-1,  -1,1,-1,  -1,1,1,        
                      -1,1,1,  -1,1,-1,  -1,-1,-1,  -1,-1,1,    
                      -1,-1,-1,  1,-1,-1,  1,-1,1,  -1,-1,1,   
                      1,-1,-1,  -1,-1,-1,  -1,1,-1,  1,1,-1]   

	#~ nedges = [0,0,1,  0,0,1,  0,0,1,  0,0,1,             
                     #~ 1,0,0,  1,0,0,  1,0,0, 1,0,0,            
                     #~ 0,1,0,  0,1,0,  0,1,0, 0,1,0,            
                     #~ -1,0,0,  -1,0,0, -1,0,0,  -1,0,0,        
                     #~ 0,-1,0,  0,-1,0,  0,-1,0,  0,-1,0,       
                     #~ 0,0,-1,  0,0,-1,  0,0,-1,  0,0,-1]
	#~ 
	
	texedges = [0,0, 1,0, 1,1, 0,1,
		    1,0, 1,1, 0,1, 0,0,
		    0,1, 0,0, 1,0, 1,1,
		    1,1, 0,1, 0,0, 1,0,
		    1,0, 1,1, 0,1, 0,0,
		    0,0, 1,0, 1,1, 0,1]
		    
	glEnableClientState(GL_VERTEX_ARRAY)
        #~ glEnableClientState(GL_NORMAL_ARRAY)
	glEnableClientState(GL_TEXTURE_COORD_ARRAY)	
			
	#~ nedges = NormEdge(vedges)
	
	glVertexPointer(3,GL_FLOAT,0,vedges)
	#~ glNormalPointer(GL_FLOAT,0,nedges)
	glTexCoordPointer(2,GL_FLOAT,0,texedges)
	glDrawArrays(GL_QUADS,0,4*6)
	
        glDisableClientState(GL_TEXTURE_COORD_ARRAY)
	#~ glDisableClientState(GL_NORMAL_ARRAY)
        glDisableClientState(GL_VERTEX_ARRAY)
	
	glEndList()
    
#~ нарисовать 1н раз!!!
def drawCoast():
    setTexture('pic/coast.png')
    #~ setTexture('pic/sun.png')
    glPushMatrix()
    #~ отраженный цвет матриала (коричневый)
    glMaterialfv(GL_BACK,GL_SPECULAR,(0.6,0.7,0.1,1))
    #~ коэффициент зеркального отражения (максимум зеркального блика)
    glMaterialf(GL_BACK,GL_SHININESS,128)
    
    glTranslate(BORDER,BORDER/2,-0.5)
    glScale(2,BORDER/2,1.5)
    drawCube()
    glPopMatrix()
    
def mouse(x,y):
    global prevx,prevy
    dx=prevx-x
    dy=prevy-y
    camera.yaw+=dx*0.01
    camera.pitch+=dy*0.01
    #~ pi2 = atan(1)*2
    pi4 = atan(1)*4
    #~ if camera.pitch>pi2: camera.pitch=pi2
    #~ if camera.pitch<-pi2: camera.pitch=-pi2
    if camera.pitch>pi4: camera.pitch=pi4
    if camera.pitch<-pi4: camera.pitch=-pi4
    prevx=x
    prevy=y


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
    
    
def drawGenerator():
    global alphaIco
    alphaIco += 0.5
    
    glPushMatrix()
    
    #~ отраженный цвет матриала (белый)
    glMaterialfv(GL_FRONT,GL_SPECULAR,(0.8,0.9,0.9,1))
    #~ коэффициент зеркального отражения (максимум зеркального блика)
    glMaterialf(GL_FRONT,GL_SHININESS,128)
    
    glDisable(GL_TEXTURE_2D)
    glTranslate(5,5,3.5)
    glScale(2,2,2)
    glRotatef(alphaIco,0,0,1)
    glutSolidIcosahedron(quadratic)
    #~ gluCylinder(quadratic,1.0,0.0,3.0,32,32)
    glEnable(GL_TEXTURE_2D)
    glPopMatrix()

def drawNLO(x=10,y=35):
    
    global quadratic
    quadratic = gluNewQuadric() 
    #~ Создаем плавные нормали ( НОВОЕ )
    gluQuadricNormals(quadratic, GLU_SMOOTH) 
    #~ Создаем координаты текстуры ( НОВОЕ )   
    gluQuadricTexture(quadratic, GL_TRUE)
    gluQuadricDrawStyle(quadratic, GLU_FILL);
    
    setTexture('pic/nlo.png')
    
    #~ прожекторный свет
    #~ glEnable(GL_LIGHT2)
    #~ glLightfv(GL_LIGHT2,GL_POSITION,(30,10,4,1))
    #~ glLightfv(GL_LIGHT2,GL_SPOT_CUTOFF,10.0)
    #~ glLightfv(GL_LIGHT2,GL_SPOT_DIRECTION,(0,1,-1))
    #~ glLightfv(GL_LIGHT2,GL_SPOT_EXPONENT,10.0)
    
    glPushMatrix()
    #~ отраженный цвет матриала (белый)
    glMaterialfv(GL_BACK,GL_SPECULAR,(1,1,1,1))
    #~ коэффициент зеркального отражения (максимум зеркального блика)
    glMaterialf(GL_BACK,GL_SHININESS,128)
    
    global stateBorder
    if stateBorder:
	glTranslate(nloX,nloY,4)
    else:
	glTranslate(10,35,4)
    glRotatef(20,1,0,0)
    glRotatef(alphaSun*5,0,0,1)
    #~ glMaterialfv(GL_BACK,GL_EMISSION,(0.3,0.2,0.2,0.0))
    #~ glutSolidTorus(0.5,1.5,16,20)
    gluDisk(quadratic,1.0,3.0,32,32)
    glPopMatrix()
    
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
    if k=='q' or k=='\x1b':
        looping=False
    keys[k]=True

def createClouds(sprites):
    for i in xrange(20):
      s=Sprite()
      s.x=randint(5,35)
      s.y=randint(5,35)
      s.z = 6.0
      s.tex='pic/cloud.png'
      sprites += [s]
      
def createTrees(sprites):
    for i in xrange(20):
      s=Sprite()
      s.x=randint(BORDER-1,BORDER+1)
      s.y=randint(2,38)
      s.tex='pic/tree.png'
      sprites += [s]    
      
def createShips(sprites):
    for tex in ('ships/ship0.png','ships/ship2.png','ships/ship1.png'):
	for i in xrange(10):
	  s=Sprite()
	  s.x=randint(5,35)
	  s.y=randint(5,35)
	  s.z = FSurf(s.x,s.y)-0.2
	  s.tex=tex
	  sprites += [s]

def createSprites():
    global sprites
    sprites += [Sprite()]
    createClouds(sprites)
    createTrees(sprites)
    createShips(sprites)

def InitGL(Width, Height):                # We call this right after our OpenGL window is created.
	glClearColor(0.0, 0.0, 0.0, 0.0)    # This Will Clear The Background Color To Black
	glClearDepth(1.0)                    # Enables Clearing Of The Depth Buffer
	glShadeModel(GL_SMOOTH)                # Enables Smooth Color Shading
 
	glMatrixMode(GL_PROJECTION)
	glLoadIdentity()                    # Reset The Projection Matrix
										# Calculate The Aspect Ratio Of The Window
	gluPerspective(45.0, float(Width)/float(Height), 0.1, 100.0)
 
	glMatrixMode(GL_MODELVIEW)
 
	if not glUseProgram:
		print 'Missing Shader Objects!'
		sys.exit(1)
 
	global program
	program = compileProgram(
		compileShader(open("sea_vert.glsl"),GL_VERTEX_SHADER),
		compileShader(open("sea_frag.glsl"),GL_FRAGMENT_SHADER),
	)	
		


inited = False
def initOnce():
    global inited,sprites
    if inited: return
    inited = True
    
    InitGL(800, 600)
    glUseProgram(program)
    
    createSprites()
	
#~ 
#~ pos = 1.0
#~ def setLight():
	#~ global pos
	#~ if program:
		#~ lightPos = glGetUniformLocation(program, "lightPos")
		#~ if not lightPos in (None,-1):
			#~ pos = pos + 0.1
			#~ glUniform3f(lightPos,pos,pos,pos)

def setLightShader():
	if program:
		pos = glGetUniformLocation(program, "initLightPos")
		if not pos in (None,-1):
			glUniform3f(pos,10,10,10)
			
		pos = glGetUniformLocation(program, "lightPos")
		if not pos in (None,-1):
			glUniform4f(pos,100,100,100,1)	
		
		pos = glGetUniformLocation(program, "eyePos")
		if not pos in (None,-1):
			glUniform4f(pos,100,100,100,1)	

		pos = glGetUniformLocation(program, "lightPosb")
		newpos = -alphaSun
		if 50 < newpos%100 < 100:
			newpos = (-alphaSun)%100
		if not pos in (None,-1):
			glUniform4f(pos,newpos,newpos,newpos,1)	
			
		pos = glGetUniformLocation(program, "eyePosb")
		if not pos in (None,-1):
			glUniform4f(pos,100,100,100,0)	

def setTexShader(glslName="tex1",idTex=0):
	if program:
		tex = glGetUniformLocation(program, glslName)
		if not tex in (None,-1):
			glUniform1i(tex,idTex)


def display():
    initOnce()
    global eltime
    curtime=glutGet(GLUT_ELAPSED_TIME)
    #~ разница подгрузки
    dt=curtime-eltime
    curtime=eltime
    
    camera.move(dt)
    
    glClearColor(0.3,0.6,0.7,1.0)
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
    #~ glEnable(GL_NORMALIZE)
    #~ glEnable(GL_LIGHTING)
    #~ setupLight()
    
    glEnable(GL_TEXTURE_2D)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST) # GL_LINEAR
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
    glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
    
    setLightShader()
    setTexShader("decalMap",0)
    #~ морские волны (карта высот)
    drawSurface()
    #~ берег
    drawCoast()
    #~ солнце
    drawSun()
    
    #~ источник кораблей
 
    drawGenerator()
    
    #~ нло
    drawNLO()
    
    #~ рисуем корабли и задаем траекторию движения
    
    F0 = lambda x: cos(1.5*x)
    F1 = lambda x: 4*sin(2.5*x)
    F2 = lambda x: 4*tan(2.5*x)
    
    for s in sprites:
	s.draw()
	if s.tex == 'ships/ship0.png':
	    s.move(F0)
	elif s.tex == 'ships/ship1.png':
	    s.move(F1)
	elif s.tex == 'ships/ship2.png':
	    s.move(F2)
    
    len_s = len(sprites)
    #~ магическое число 45 появилось, т.к. мы считаем кол-во всех спрайтов 
    #~ вместе с облаками и деревьями, а удаляли только кораблики
    if len_s<=45:
	del sprites[:]
	createSprites()
	
    glutSwapBuffers()
	
		
	 
def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE|GLUT_RGBA|GLUT_DEPTH)
    glutInitWindowSize(800,600)
    glutCreateWindow('sea')
    
    glutDisplayFunc(display)
    glutKeyboardFunc(kbd_down)
    glutKeyboardUpFunc(kbd_up)
    glutPassiveMotionFunc(mouse)
    
    #~ InitGL(800, 600)
    #~ glUseProgram(program)
    
    while(looping):
        glutMainLoopEvent()
        glutPostRedisplay()
    pass

if __name__ == "__main__":
	main()

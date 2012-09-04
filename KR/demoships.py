#!/usr/bin/python
# -*- coding: utf-8 -*-

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
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
#~ Создаем указатель на квадратичный объект
quadratic=0
sprites=[]

stateBorder = False
nloX = 0
nloY = 0

def FSurf(x,y):    
	return sin(0.3*x)+sin(0.7*y)*sin(0.5*y)


def checkSurface(cx,cy,cz):	
    """Если столкнулись с "волнами", то возвращаем значение координаты z,
    иначе оставляем ее как есть"""	
    de = 0.25
    z = cz
    if (cz-FSurf(cx,cy)) < de:
	z = FSurf(cx,cy)+de
    return z

def checkArch(sx,sy):
    """Проверка на столкновение с аркой (входит ли в область 
    2х окружностей). Возвращаем значения х и y, в которых 
    "произввести столкновение". """
    
    by1 = BORDER/2-5.0
    bx1 = BORDER/2
    by2 = BORDER/2+5.0
    bx2 = BORDER/2
    
    if ((sx-bx1)**2+(sy-by1)**2 < 2.**2) or ((sx-bx2)**2+(sy-by2)**2 < 2.**2) :
	#~ print("I'm here")
	sx -= 0.5
	sy -= 0.5
    
    return sx,sy


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
		self.x = BORDER/2+10 # 10
		self.y = 5
		self.z = 1.5
		self.vx = self.vy = self.vz = .0
		self.yaw = 280.0
		#~ self.yaw = 20.0
		self.pitch = -0.7
		self.goA = self.goD = self.goW = self.goS = False
	
	def move(self,dt):
		speed = 0.00005
		svx, svy, svz = self.vx, self.vy, self.vz
		sx, sy, sz = self.x, self.y, self.z
		
		if self.goW:
			svx=cos(self.yaw)*cos(self.pitch)
			svy=sin(self.yaw)*cos(self.pitch)
			svz=sin(self.pitch)

		if self.goS:
			svx=-cos(self.yaw)*cos(self.pitch)
			svy=-sin(self.yaw)*cos(self.pitch)
			svz=-sin(self.pitch)
        
		if self.goA:
			svx=-sin(self.yaw)*cos(self.pitch)
			svy=cos(self.yaw)*cos(self.pitch)
			
		if self.goD:
			svx=sin(self.yaw)*cos(self.pitch)
			svy=-cos(self.yaw)*cos(self.pitch)
		
		svx*=speed
		svy*=speed
		svz*=speed
		self.vx, self.vy, self.vz = svx, svy, svz
		
		sx+=svx*dt
		sy+=svy*dt
		sz+=svz*dt
		
		sz = checkSurface(sx,sy,sz)
		sx,sy,sz = checkBorder(sx,sy,sz)
		sx,sy = checkArch(sx,sy)
		sx,sy = checkIco(sx,sy)
		
		self.x,self.y,self.z = sx,sy,sz
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
	    """ Подвинули на дельту == F; если дошли до берега -- удаляем объект"""
	    global stateBorder, nloX, nloY		
	    x, y, z = self.x, self.y, self.z
	    
	    #~ проверки на столкновение
	    if (0<x<BORDER-3 and 0<y<BORDER-2):
		#~ с границей
		#~ i = random()*0.01
		i = random()*0.01
		#~ print(i)
		y += i
		x += F(i)
		z = FSurf(x,y)-0.2
		#~ с аркой
		x, y = checkArch(x,y)
		self.x, self.y, self.z = x, y, z
	    else:
		#~ используется, чтобы поставить координаты нло под приплывшим кораблем
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
    """Ставим источник, зависящий от солнца и цвет блика"""
    glEnable(GL_LIGHT1)
    #~ желтый блик от солнца
    glLightfv(GL_LIGHT1,GL_SPECULAR,(1,1,0,1))
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
    
#~ текстурные координаты вытаскиваем из обычных 
def TextureSurface(lst):
    return [lst[i] for i in xrange(len(lst)) if (i+3)%3!=0]
    
def drawSurface():
    def frange(start,end,step): 
	return map(lambda x: x*step, range(int(start*1.0/step),int(end*1.0/step)))
    
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
    alphaSun += 0.1# 0.5
    
    global quadratic
    quadratic = gluNewQuadric() 
    #~ Создаем плавные нормали
    gluQuadricNormals(quadratic, GLU_SMOOTH) 
    #~ Создаем координаты текстуры   
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
        glEnableClientState(GL_NORMAL_ARRAY)
	glEnableClientState(GL_TEXTURE_COORD_ARRAY)	
			
	nedges = NormEdge(vedges)
	
	glVertexPointer(3,GL_FLOAT,0,vedges)
	glNormalPointer(GL_FLOAT,0,nedges)
	glTexCoordPointer(2,GL_FLOAT,0,texedges)
	glDrawArrays(GL_QUADS,0,4*6)
	
        glDisableClientState(GL_TEXTURE_COORD_ARRAY)
	glDisableClientState(GL_NORMAL_ARRAY)
        glDisableClientState(GL_VERTEX_ARRAY)
	
	glEndList()
    
def drawCoast():
    setTexture('pic/coast.png')
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
    pi2 = atan(1)*2
    if camera.pitch>pi2: camera.pitch=pi2
    if camera.pitch<-pi2: camera.pitch=-pi2
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


idArch = 0
#~ Арка как экструзивная поверхность
def drawArch():
    glDisable(GL_TEXTURE_2D)
    
    glPushMatrix()
    glTranslate(BORDER/2,BORDER/2,1)
    glScalef(3,6,3)
    
    global idArch
    if idArch:
        glCallList(idArch)
    else:
        idArch=glGenLists(1)
        glNewList(idArch,GL_COMPILE_AND_EXECUTE)  
	#~ передняя пов-ть
	x = 0.0
	front1 = [x,-1.,-1., x,-0.6,-1, x,-0.6,0.2, x,-1.,0.2,
		  x,-1.,0.2, x,-0.6,0.2, x,-0.4,0.4, x,-1.,1.,
		  x,-1.,1., x,-0.4,0.4, x,0.,0.6, x,0.,1.,
		 ]
		 
	front2 = [  x,0.6,-1., x,1.,-1., x,1.,0.2, x,0.6,0.2,
		    x,0.6,0.2, x,1.,0.2, x,1.,1., x,0.4,0.4,
		    x,0.4,0.4, x,1.,1., x,0.,1., x,0.,0.6
		 ]
		 
	#~ задняя пов-ть
	step = 0.4
	back1 = []
	for i,x in enumerate(front1):
	    if (i+3)%3 == 0:
		back1.append(x+step)
	    else:
		back1.append(x)
		
	back2 = []
	for i,x in enumerate(front2):
	    if (i+3)%3 == 0:
		back2.append(x+step)
	    else:
		back2.append(x)
	
	x0 = x+step
	
	#~ собираемся по 3 координаты
	def in_coords(lst):
	    return [ (lst[i],lst[i+1],lst[i+2]) 
			for i in xrange(len(lst)-2) if (i+3)%3 == 0 ]
	    
	#~ извлекаем поэлементно точки x y z
	def elem_of(lst):
	    return lst[0],lst[1],lst[2]
		    
	#~ преобразовываем списки вершин к виду [(x,y,z),(x,y,z),...]
	p_front1,p_front2,p_back1,p_back2 = [in_coords(l) 
		    for l in [front1,front2,back1,back2]]	
	
	#берем по паре из каждого списка вершин, чтобы сделать экструзию
	    
	serfArch = [] 
	#~ магические цифры расшифровываются из рисунка 
	#~ (направление обхода против часовой)
	serfArch.extend(p_front1[0])
	serfArch.extend(p_front1[7])
	serfArch.extend(p_back1[7])
	serfArch.extend(p_back1[0])
	
	#~ right
	serfArch.extend(p_front2[1])
	serfArch.extend(p_front2[6])
	serfArch.extend(p_back2[6])
	serfArch.extend(p_back2[1])
	
	#~ top
	serfArch.extend(p_front1[8])
	serfArch.extend(p_front2[6])
	serfArch.extend(p_back2[6])
	serfArch.extend(p_back1[8])
	
	#~ bottom
	serfArchB0 = []
	serfArchB0.extend(p_front1[1])
	serfArchB0.extend(p_front1[2])
	serfArchB0.extend(p_back1[2])
	serfArchB0.extend(p_back1[1])
	
	serfArchB0.extend(p_front1[2])
	serfArchB0.extend(p_front1[4])
	serfArchB0.extend(p_back1[4])
	serfArchB0.extend(p_back1[2])
	
	serfArchB0.extend(p_front1[9])
	serfArchB0.extend(p_front1[10])
	serfArchB0.extend(p_back1[10])
	serfArchB0.extend(p_back1[9])
	
	serfArchB1=[]
	serfArchB1.extend(p_front2[11])
	serfArchB1.extend(p_front2[7])
	serfArchB1.extend(p_back2[7])
	serfArchB1.extend(p_back2[11])
	
	serfArchB1.extend(p_front2[8])
	serfArchB1.extend(p_front2[4])
	serfArchB1.extend(p_back2[4])
	serfArchB1.extend(p_back2[8])
	
	serfArchB1.extend(p_front2[3])
	serfArchB1.extend(p_front2[0])
	serfArchB1.extend(p_back2[0])
	serfArchB1.extend(p_back2[3])
	
	arch = [front1,front2,back1,back2,serfArch,serfArchB0,serfArchB1]
	color = [1,0,0]
	
	glEnableClientState(GL_VERTEX_ARRAY)
	glEnableClientState(GL_NORMAL_ARRAY)
	glEnableClientState(GL_COLOR_ARRAY)
	
	for l in arch:
	    glVertexPointer(3,GL_FLOAT,0,l)
	    glNormalPointer(GL_FLOAT,0,NormEdge(l))
	    glColorPointer(3,GL_FLOAT,0,color)
	    glDrawArrays(GL_QUADS,0,12)
	
	glDisableClientState(GL_COLOR_ARRAY)
	glDisableClientState(GL_NORMAL_ARRAY)
	glDisableClientState(GL_VERTEX_ARRAY)
	
	glEndList()
	
    glPopMatrix()
    glEnable(GL_TEXTURE_2D)
    
    
def drawGenerator():
    global alphaIco
    alphaIco += 0.5
    
    glPushMatrix()
    
    #~ отраженный цвет матриала (почти белый)
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
    #~ Создаем плавные нормали
    gluQuadricNormals(quadratic, GLU_SMOOTH) 
    #~ Создаем координаты текстуры   
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
    if k=='q':
        looping=False
    keys[k]=True

def createClouds(sprites):
    for i in xrange(20):
      s=Sprite()
      s.x=randint(5,35)
      s.y=randint(5,35)
      s.z = 6.0
      s.tex='pic/stars.png'
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


#~ --------------------------------------------------------

class Particle:
    def __init__(self,x=0.0,y=0.0,z=0.0):
        
	#~ активна ли частица?
        self.active=True
	#~ длина жизни
        self.life=1.0 
	#~ шаг затухания
        self.fade=0.0 
    
	#~ свет частицы
        self.r=0.0 
        self.g=0.0 
        self.b=0.0 
        
	#~ позиция на экране
        self.x=x 
        self.y=y 
        self.z=z 
        
	#~ направления движения
        self.xi=0.0 
        self.yi=0.0 
        self.zi=0.0 
        
	#~ гравитация
        self.xj=0.0 
        self.yj=0.0 
        self.zj=0.0 

class ColorParticle(object):
    def __init__(self, r = 0, g = 0, b = 0):
	self.r = r
	self.g = g
	self.b = b

MAX_PARTICLES = 2000
	
	
def getColorFire(totalIntens):
    curcolor = ColorParticle()
    paint = [0 for j in xrange(totalIntens) for i in xrange(3)]
    for i in xrange(3):
	for j in xrange(totalIntens):
	    if i == 0:
		curcolor = ColorParticle(j)
	    elif i == 1:
		curcolor = ColorParticle(totalIntens,j)
	    elif i == 2:
		curcolor = ColorParticle(totalIntens,totalIntens,j)
		
	    paint[totalIntens*i+j] = curcolor
    return paint

fireprts = [Particle() for i in xrange(MAX_PARTICLES)]
firecolor = getColorFire(255)


def Fire(prts, color):
    
    #~ массив из "частичек"
    #~ prts = [Particle() for i in xrange(MAX_PARTICLES)]
    
    ncol = len(color)
    #~ for c in color:
	#~ print(c.r,c.g,c.b)
    
    for i in xrange(MAX_PARTICLES):
	prts[i].life = 1.0
	prts[i].active = True
	prts[i].fade=float(randrange(0,100))/1000.0+0.01
	
	prts[i].xi=(float(randrange(0,60))-32.0)
        prts[i].yi=(float(randrange(0,90))-30.0)
        prts[i].zi=(float(randrange(0,60))-32.0)
	
	prts[i].r = color[-1].r
	prts[i].g = color[-1].g
	prts[i].b = color[-1].b
	
	#~ prts[i].r = 1
	#~ prts[i].g = 1
	#~ prts[i].b = 0 
	
	#~ print(prts[i].r,prts[i].g,prts[i].b)
	
	prts[i].xg = 0.0
	prts[i].yg = 0.8
	prts[i].zg = 0.0
	
    
def drawFire(pos=[0,0,0], prts=[], color=[]):
    
    #~ замедление
    slowdown = 0.5
    #~ увеличение
    zoom = -30.0
    
    ncol = len(color)
    
    slowdown = slowdown*MAX_PARTICLES
    
    for i in xrange(MAX_PARTICLES):
	#~ print(prts[i].r,prts[i].g,prts[i].b)
	
	
	if prts[i].active:
	    x,y,z = pos[0]+prts[i].x, pos[1]+prts[i].y, pos[2]+prts[i].z
	    #~ print(x,y,z)
	    
	    #~ цвет зависит от времени жизни; при "зарождении" - белый, ближе к угасанию -- оранжевый и желтый
	    lifelen = max(prts[i].life-0.2,0.0)
	    #~ print(prts[i].life,prts[i].fade)
	    
	    lf = (int)(lifelen*ncol)
	    #~ print (lf)
	    curcolor = color[lf%ncol]
	    
	    #~ print(curcolor.r, curcolor.g, curcolor.b)
	    glColor4f(curcolor.r, curcolor.g, curcolor.b, prts[i].life)
	    #~ glColor4f(prts[i].r,prts[i].g,prts[i].b,prts[i].life)
	    setTexture("pic/fire.bmp")
	    
	    r = 0.7
	    glBegin(GL_TRIANGLE_STRIP)
	    glTexCoord2d(1,1)
	    glVertex3f(x+r, y+r, z)
	    glTexCoord2d(0,1)
	    glVertex3f(x-r, y+r, z)
	    glTexCoord2d(1,0)
	    glVertex3f(x+r, y-r, z)
	    glTexCoord2d(0,0)
	    glVertex3f(x-r, y-r, z)
	    glEnd()
	    
	    #~ меняем уровень жизни и свойства частицы
	    prts[i].x += prts[i].xi/slowdown
	    prts[i].y += prts[i].yi/slowdown
	    prts[i].z += prts[i].zi/slowdown
	    
	    prts[i].xi += prts[i].xg
	    prts[i].yi += prts[i].yg
	    prts[i].zi += prts[i].zg
	    prts[i].life -= prts[i].fade
	    
	    if prts[i].life<0:
		#~ оживляем
		prts[i].life=1.0
                prts[i].fade=float(randrange(0,100))/1000.0+0.01
                
                prts[i].x=0.0
                prts[i].y=0.0
                prts[i].z=0.0
                
                prts[i].xi=float((randrange(0,60))-32.0)
                prts[i].yi=float((randrange(0,90))-20.0)
                prts[i].zi=float((randrange(0,60))-30.0)
		
		prts[i].r = color[i%ncol].r
		prts[i].g = color[i%ncol].g
		prts[i].b = color[i%ncol].b
		prts[i].life -= prts[i].fade
		#~ 
		#~ prts[i].r = 1
		#~ prts[i].g = 1
		#~ prts[i].b = 0    

    
#~ ----------------------------------------------------------

def getColorBlowOut(totalIntens):
    curcolor = ColorParticle()
    paint = [0 for j in xrange(totalIntens) for i in xrange(2)]
    for i in xrange(2):
	for j in xrange(totalIntens):
	    if i == 0:
		curcolor = ColorParticle(0,0,j)
	    elif i == 1:
		curcolor = ColorParticle(0,j,totalIntens)
	    #~ elif i == 2:
		#~ curcolor = ColorParticle(0,j,0)
	    paint[totalIntens*i+j] = curcolor
    return paint
    

waterprts = [Particle(0,0,0) for i in xrange(MAX_PARTICLES)] 
watercolor = getColorBlowOut(255)


def BlowOut(prts, color):
    
    ncol = len(color)
    
    for i in xrange(MAX_PARTICLES):
	prts[i].life = 1.0
	prts[i].active = True
	prts[i].fade=float(randrange(0,100))/1000.0+0.1
	
	#~ explode
	prts[i].xi=(float(randrange(0,50))-22.0)*5
        prts[i].yi=(float(randrange(0,50))-25.0)*5
        prts[i].zi=(float(randrange(0,50))-25.0)*5
	
	prts[i].r = color[-1].r
	prts[i].g = color[-1].g
	prts[i].b = color[-1].b

	prts[i].xg = 1.0
	prts[i].yg = -1.3
	prts[i].zg = 0.0



def drawBlowOut(pos=[0,0,0], prts=[], color=[]):
    
    #~ замедление
    slowdown = 0.5
    #~ увеличение
    zoom = -30.0
    
    ncol = len(color)
    slowdown = slowdown*MAX_PARTICLES
    
    for i in xrange(MAX_PARTICLES):
	#~ print(prts[i].r,prts[i].g,prts[i].b)
	
	if prts[i].active:
	    x,z = pos[0]+prts[i].x, pos[1]+prts[i].z
	    y = pos[2]-(0.5*prts[i].x)**4
	    #~ if i>200:
		#~ y = pos[2]+7*sin((0.5*prts[i].x)**4)
	    #~ else:
		#~ y = prts[i].y*5
		
	    if i%2:
		x = -prts[i].x
	    else:
		x = prts[i].x
	    #~ цвет зависит от времени жизни; при "зарождении" - белый, ближе к угасанию -- оранжевый и желтый
	    lifelen = max(prts[i].life-0.2,0.0)
	    
	    lf = (int)(lifelen*ncol)
	    curcolor = color[lf%ncol]
	    
	    #~ glColor4f(curcolor.r, curcolor.g, curcolor.b, prts[i].life)
	    glColor4f(prts[i].r,prts[i].g,prts[i].b,prts[i].life)
	    setTexture("pic/kaplya.png")
	    
	    r = 0.3
	    glBegin(GL_TRIANGLE_STRIP)
	    glTexCoord2d(1,1)
	    glVertex3f(x+r, y+r, z)
	    glTexCoord2d(0,1)
	    glVertex3f(x-r, y+r, z)
	    glTexCoord2d(1,0)
	    glVertex3f(x+r, y-r, z)
	    glTexCoord2d(0,0)
	    glVertex3f(x-r, y-r, z)
	    glEnd()
	    
	    #~ меняем уровень жизни и свойства частицы
	    prts[i].x += prts[i].xi/slowdown
	    prts[i].y += prts[i].yi/slowdown
	    prts[i].z += prts[i].zi/slowdown
	    
	    #~ prts[i].z += sin(prts[i].xi)
	    
	    prts[i].xi += prts[i].xg
	    prts[i].yi += prts[i].yg
	    prts[i].zi += prts[i].zg
	    prts[i].life -= prts[i].fade
	    
	    if prts[i].life<0:
		#~ оживляем
		prts[i].life=1.0
                prts[i].fade=float(randrange(0,100))/1000.0+0.01
		if z>FSurf(x,y):
		    prts[i].fade=1.0
		#~ if i<200 and i>700:
		prts[i].x=0.0
		prts[i].y=0.0
		prts[i].z=0.0
                
                prts[i].xi=float((randrange(0,60)-22)/100.0)*1.5
                prts[i].yi=float((randrange(0,50)-20)/100.0)*1.5
		prts[i].zi=float((randrange(0,60)-21)/100.0)
		
		prts[i].r = color[i%ncol].r
		prts[i].g = color[i%ncol].g
		prts[i].b = color[i%ncol].b
		prts[i].life -= prts[i].fade

#~ --------------------------------------------------------------








inited = False
def initOnce():
    global inited,sprites
    if inited: return
    inited = True
    createSprites()
    
    global fireprts, firecolor
    global waterprts, watercolor
    Fire(fireprts,firecolor)
    BlowOut(waterprts,watercolor)

def display():
    initOnce()
    global eltime
    curtime=glutGet(GLUT_ELAPSED_TIME)
    #~ разница подгрузки
    dt=curtime-eltime
    curtime=eltime
    
    camera.move(dt)
    
    glClearColor(0.0,0.0,0.0,0.0)
    #~ glClearColor(0.3,0.6,0.7,1.0)
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
    glEnable(GL_LIGHTING)
    setupLight()
    
    glEnable(GL_TEXTURE_2D)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST) # GL_LINEAR
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
    glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
    
    #~ морские волны (карта высот)
    drawSurface()
    #~ берег
    drawCoast()
    #~ солнце
    #~ drawSun()
    
    #~ источник кораблей
    #~ drawGenerator()
    
    #~ нло
    drawNLO()
    
    glDisable(GL_CULL_FACE)
    #~ арка
    drawArch()
    
    #~ рисуем корабли и задаем траекторию движения
    
    F0 = lambda x: cos(3*x)
    F1 = lambda x: 4*sin(5*x)
    F2 = lambda x: 4*tan(5*x)
    
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
	
	
	#~ -------------------------------------------------------------------
	
    global fireprts,firecolor
    global waterprts,watercolor
    
    glDisable(GL_CULL_FACE)
    glDisable(GL_NORMALIZE)
    glDisable(GL_LIGHTING)
    glDisable(GL_TEXTURE_2D)
    
    glDepthFunc(GL_LESS)                # The Type Of Depth Test To Do
    glDisable(GL_DEPTH_TEST)                # Enables Depth Testing
    glEnable(GL_BLEND)         
    glShadeModel(GL_SMOOTH)                # Enables Smooth Color Shading
    
    glBlendFunc(GL_SRC_ALPHA,GL_ONE) 
    glHint(GL_PERSPECTIVE_CORRECTION_HINT,GL_NICEST)
    glHint(GL_POINT_SMOOTH_HINT,GL_NICEST) 
    glEnable(GL_TEXTURE_2D)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST) # GL_LINEAR
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
    glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
    
    #~ glRotatef(0, 0.0, 1.0, 0.0)
    glPushMatrix()
    global stateBorder
    if stateBorder:
	glTranslate(nloX,nloY,-1)
    
    glScale(1,0.5,0.5)
    glRotatef(90, 1.0, 0.0, 0.0)
    #~ glRotatef(0, 0.0, 0.0, 1.0)
    drawFire([0,0,0],fireprts,firecolor)
    glPopMatrix()
    

    glPushMatrix()
    #~ glTranslate(0.0,0.0,2.5)
    glTranslate(3,3,2.5)
    #~ glTranslate(BORDER/2,BORDER/2,4.5)
    glScale(0.5,0.5,1.5)
    glRotatef(90+camera.yaw*180/(atan(1)*4),0,0,1)
    glRotatef(90, 1.0, 0.0, 0.0)
    
    drawBlowOut([0,0,0],waterprts,watercolor)
    glPopMatrix()
    
    glDisable(GL_BLEND)
    glEnable(GL_DEPTH_TEST)
	
	#~ ----------------------------------------------
    glutSwapBuffers()
	 
def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE|GLUT_RGBA|GLUT_DEPTH)
    glutInitWindowSize(800,600)
    glutCreateWindow('demoShips')
    
    glutDisplayFunc(display)
    glutKeyboardFunc(kbd_down)
    glutKeyboardUpFunc(kbd_up)
    glutPassiveMotionFunc(mouse)
    while(looping):
        glutMainLoopEvent()
        glutPostRedisplay()
    pass

if __name__ == "__main__":
	main()

#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from PyQt4 import QtCore, QtGui, QtOpenGL
from widget import Ui_Widget
from math import * 
from itertools import izip
from numpy import *

#~ Класс используемых матриц
class qtMatrix(object):
	def __init__(self):
		pass
	
	#~ повороты
	def rotateX(self,a):
		s = sin(a)
		c = cos(a)
		return QtGui.QMatrix4x4(1, 0, 0, 0,
								0, c, -s, 0,
								0, s, c, 0,
								0, 0, 0, 1)
		
	def rotateY(self,a):
		s = sin(a)
		c = cos(a)
		return QtGui.QMatrix4x4(c, 0, s, 0,
								0, 1, 0, 0,
								-s, 0, c, 0,
								0, 0, 0, 1)
		
	def rotateZ(self,a):
		s = sin(a)
		c = cos(a)
		return QtGui.QMatrix4x4(c, -s, 0, 0,
								s, c, 0, 0,
								0, 0, 1, 0,
								0, 0, 0, 1)

	#~ масштабирование
	def scale(self,k=60):
		return QtGui.QMatrix4x4(k,0,0,0,
								0,k,0,0,
								0,0,k,0,
								0,0,0,1)
	#~ передвижение
	def translate(self,x=0,y=0,z=0):
		return QtGui.QMatrix4x4(1,0,0,x,
								0,1,0,y,
								0,0,1,z,
								0,0,0,1)
								
	#~ [v[0], -v[2], v[1], 0]
	#~ обмен координат
	@property
	def exchange(self):
		return QtGui.QMatrix4x4(1,0,0,0,
								0,0,-1,0,
								0,1,0,0,
								0,0,0,1)
				
	#~ установка камеры			
	def lookAt(	self, 
				eyeX=5, eyeY=4, eyeZ=3, 
				centerX=0, centerY=0, centerZ=0, 
				upX=0, upY=1, upZ=0):
		
		normalize = lambda vect: vect*1.0/sqrt(vect.x()**2+vect.y()**2+vect.z()**2)		
		
		F = QtGui.QVector4D(centerX-eyeX, centerY-eyeY, centerZ-eyeZ, 0)
		UP = QtGui.QVector4D(upX, upY, upZ, 0)
		f = normalize(F)
		up = normalize(UP)
		s = f*up
		u = s*f
		
		matr = QtGui.QMatrix4x4(s.x(), s.y(), s.z(), 0,
								u.x(), u.y(), u.z(), 0,
								-f.x(), -f.y(), -f.z(), 0,
								0, 0, 0, 1)
		return matr
		
	#~ перспектива (-)
	def perspective(self,N,z):
		m = QtGui.QMatrix4x4(1, 0, 0, 0,
							 0, 1, 0, 0,
							 0, 0, 1, 0,
							 0, 0, 0, 1)
		return self.scale(N/z)*m
	
	#~ перспектива с матрицей из OpenGL
	def qt_perspective(self):
		#consts
		N = 3.0
		angle = 120.0
		aspect = 1.0
		F = 1.0
				
		pi = 4*atan(1)
		top = N*tan(pi/180*angle/2)
		bott = -top
		right = top*aspect
		left = -right
		matr = QtGui.QMatrix4x4(2*N/(right-left), 0, (right+left)/(right-left), 0,
								0, 2*N/(top-bott), (top+bott)/(top-bott), 0,
								0, 0, -(F+N)/(F-N), -2*F*N/(F-N),
								0, 0, -1, 0)
		return matr
				
	
class Widget(QtGui.QWidget):
	def __init__(self, parent=None):
		QtGui.QWidget.__init__(self, parent)
        
		self.center()
		self.ui = Ui_Widget()
		self.ui.setupUi(self)
		self.alpha = 0.0
		self.betta = 0.0
		self.sc = 1.0
		
		#создание тора
		self.Torus = makeTorus()
		self.amount = len(self.Torus)-1
		self.matr = qtMatrix()
		
	def center(self):
		screen = QtGui.QDesktopWidget().screenGeometry()
		size =  self.geometry()
		self.move((screen.width()-size.width())/2, (screen.height()-size.height())/2)	
		
	def mouseMoveEvent(self, event):
		x, y = event.pos().x(), event.pos().y()
		if 0<0.5*x<360 and 0<0.5*y<360:
			#~ print(x,y)
			self.alpha = 0.01*x
			self.betta = 0.01*y
		self.update()
	
	#~ масштабирование по "+", "-" 
	def keyPressEvent(self,event):
		st = 0.25
		if event.key() == QtCore.Qt.Key_Plus and self.sc+st > 0:
			self.sc += st
			#~ print(self.sc)
			self.update()
			
		elif event.key() == QtCore.Qt.Key_Minus and self.sc-st > 0:
			self.sc -= st
			#~ print(self.sc)
			self.update()
	
	
	def paintEvent(self, event):
		
		size = self.size()
		ox = size.width()/2
		oy = size.height()/2	
		
		matr = self.matr
		
		#~ объявление всех матриц для использования
		k=60
		matrScale = matr.scale(k*self.sc)
		matrRZ = matr.rotateZ(self.alpha)
		matrRX = matr.rotateX(self.betta)
		vectTrans = QtGui.QVector4D(ox,oy,0,0)	
		
		#~ получение "перспективных" вершин
		vect_Torus = self.Torus
		if self.ui.checkBox.isChecked():
			vect_Torus = [vect_perspective(matr,self.Torus[i]) for i in range(0, self.amount+1)]
		
		#~ общая матрица
		matrTotal = matrRZ*matrRX*matr.exchange*matrScale

		#~ камера применяется почти в конце
		if self.ui.checkBox_2.isChecked():
			matrTotal *= matr.lookAt()
		
		paint = QtGui.QPainter()
		
		paint.begin(self)
		paint.setPen(QtCore.Qt.blue)
		#~ каждый вектор умножается на общую матрицу и "немного" сдвигается
		for i in range(0, self.amount, 2):
			v1 = vect_Torus[i+0]*matrTotal
			v2 = vect_Torus[i+1]*matrTotal
			v1 += vectTrans
			v2 += vectTrans
			paint.drawLine(v1.x(),v1.y(),v2.x(),v2.y())
			
		paint.end()
		self.update()

def formulTorus(v, u, D = 2.0, A = 1.0):
	return QtGui.QVector4D((D+A*cos(v))*cos(u), (D+A*cos(v))*sin(u), A*sin(v), 1)

def makeTorus():	
	def frange(start,end,step): 
		return map(lambda x: x*step, range(int(start*1.0/step),int(end*1.0/step)))

	points = []
	pi = atan(1)*4
	st = 0.5
	st = pi / int(pi / st)
	
	for a in frange(-pi-st, pi+st, st):
		for b in frange(-pi-st, pi+st, st):
			ltmp = [formulTorus(v,u) 
					for v,u in ((a,b), (a+st,b),
						(a+st,b), (a+st,b+st),
						(a+st, b+st), (a+st,b),
						(a+st,b), (a,b))
					]
			points.extend(ltmp)
						
	return points

def vect_perspective(matr,v):
	v *= matr.scale(2.3/(-v.z()-4))
	return v


def main():
	app = QtGui.QApplication(sys.argv)
	w = Widget()
	w.show()
	sys.exit(app.exec_())

if __name__ == "__main__":
	main()

# -*- coding: utf-8 -*-
"""
Created on Mon Nov  5 14:11:41 2018

@author: linux
"""

import random
import array
import copy
import numpy as np

def kindToColor(kind):
    if kind == 1:
        color = (0,255,0)
    elif kind == 2:
        color = (0,0,255)
    elif kind == 3:
        color = (125,125,0)
    elif kind == 4:
        color = (0,125,125)
    elif kind == 5:
        color = (255,0,0)
    elif kind == 6:
        color = (0,125,0)
    elif kind == 7:
        color = (0,0,125)
    return color

class Tetromino:
    # Das Objektfeld sieht so aus:
    #   XXXX
    #   XXXX
    # mit x von links nach rechts
    # mit y von unten nach oben
    
    # Konstruktor für das Tetromino
    # @param1: kind ist die Art des Tetromino (0-4 und None). None bedeutet es wird ein zufälliges Tetromino erzeugt
    # @param2: color ist die Farbe als rgb-Array die der Tetromino bekommen soll. Bei None wird eine Artspezifische Farbe zugewiesen
    def __init__(self, kind, color):
        if kind is None:
            kind = random.randint(1,7)
        if color is None:
            if kind == 1:
                color = (0,255,0)
            elif kind == 2:
                color = (0,0,255)
            elif kind == 3:
                color = (125,125,0)
            elif kind == 4:
                color = (0,125,125)
            elif kind == 5:
                color = (255,0,0)
            elif kind == 6:
                color = (0,125,0)
            elif kind == 7:
                color = (0,0,125)
            
        self.color = color # color sind ja bei allen blöcken gleich und hängt eigentlich vom kind ab
        self.kind = kind
        self.__createTetromino(kind,color)
        
    def start(self):
        self.__posX=5
        self.__posY=0
        
    def moveDown(self):
        self.__posY=self.__posY+1
    
    def moveUp(self):
        self.__posY=self.__posY-1
        
    def moveRight(self):
        self.__posX=self.__posX+1
        
    def moveLeft(self):
        self.__posX=self.__posX-1
    
    def getPositions(self):
        relX, relY = np.where(self.pixels != 0)
        absX = relX+self.__posX
        absY = relY+self.__posY
        absolutePositions = np.vstack((absX, absY)) 
        #Array mit 0=>X-Position ; 1=>Y-Position die nicht leer sind
        return absolutePositions
    
    # Rotiert das Objekt und gibt das Array mit Höhen und Breitenangaben zurück
    # @param1: Anzahl der Drehungen (>0 im Uhrzeigersinn; <0 gegen den Uhrzeigersinn)
    def rotate(self, steps):
        axes = (1,0)
        if steps < 0:
            steps = -steps
            axes = (0,1)
        self.pixels = np.rot90(self.pixels,steps,axes)
    
    def copy(self,t):
        t.__posY = self.__posY
        t.__posX = self.__posX
        t.pixels = np.copy(self.pixels)
    
    def setPosX(self,value):
        self.__posX = value
    
    def trim(self):
        # Beschneide tetromino auf die kleinsmögliche breite und höhe
        # beschneide Null-zeilen und -Reihen
        self.pixels = self.pixels[:,~np.all(self.pixels==0,axis=0)]
        self.pixels = self.pixels[~np.all(self.pixels==0,axis=1)]

    def setPosY(self,value):
        self.__posY = value
    
    def __createTetromino(self, kind, color):  
        #Klassenvariable für position im Feld. Startposition oben in der Mitte
        self.__posX = 11
        self.__posY = 2
        
        self.__height = 4
        self.__width = 3
        self.pixels = np.zeros((self.__height ,self.__width))
        if kind == 1:
            self.pixels[1][0] = self.pixels[1][1] = self.pixels[1][2] = self.pixels[2][0] = 1
        elif kind == 2:
            self.pixels[0][0] = self.pixels[1][0] = self.pixels[1][1] = self.pixels[1][2] = 1
        elif kind == 3:
            self.pixels[0][1] = self.pixels[1][1] = self.pixels[1][2] = self.pixels[2][2] = 1
        elif kind == 4:
            self.pixels[0][2] = self.pixels[1][2] = self.pixels[1][1] = self.pixels[2][1] = 1
        elif kind == 5:
            self.pixels[0][2] = self.pixels[1][2] = self.pixels[2][2] = self.pixels[1][1] = 1
        elif kind == 6:
            self.pixels[0][0] = self.pixels[0][1] = self.pixels[1][0] = self.pixels[1][1] = 1
        elif kind == 7:
            self.pixels[0][0] = self.pixels[1][0] = self.pixels[2][0] = self.pixels[3][0] = 1
            
            #stefan: TODO: L BLOCK in die andere Richtung, QUadrat und vierer

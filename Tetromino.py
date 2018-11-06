# -*- coding: utf-8 -*-
"""
Created on Mon Nov  5 14:11:41 2018

@author: linux
"""

import random
import array
import copy
import numpy as np

class Tetromino:
    # Das Objektfeld sieht so aus:
    #   XXXX
    #   XXXX
    # mit x von links nach rechts
    # mit y von unten nach oben
    
    # Konstruktor für das Tetromino
    # @param1: kind ist die Art des Tetromino (0-4 und None). None bedeutet es wird ein zufälliges Tetromino erzeugt
    def __init__(self, kind, color):
        if kind is None:
            kind = random.randint(0,4)
        
        self.__kind = kind
        self.__createTetromino(kind,color)
    
    # Rotiert das Objekt und gibt das Array mit Höhen und Breitenangaben zurück
    # @param1: Anzahl der Drehungen (>0 im Uhrzeigersinn; <0 gegen den Uhrzeigersinn)
    def rotate(self, steps):
        axes = (1,0)
        if steps < 0:
            steps = -steps
            axes = (0,1)
        self.pixels = np.rot90(self.pixels,steps,axes)
        
    def __createTetromino(self, kind, color):       
        self.__height = 3
        self.__width = 3
        self.pixels = np.zeros((self.__height ,self.__width))
        if kind == 0:
            self.pixels[0][2] = self.pixels[1][2] = self.pixels[2][2] = self.pixels[1][1] = color
        elif kind == 1:
            self.pixels[1][0] = self.pixels[1][1] = self.pixels[1][2] = self.pixels[2][0] = color
        elif kind == 2:
            self.pixels[0][0] = self.pixels[1][0] = self.pixels[1][1] = self.pixels[1][2] = color
        elif kind == 3:
            self.pixels[0][1] = self.pixels[1][1] = self.pixels[1][2] = self.pixels[2][2] = color
        elif kind == 4:
            self.pixels[0][2] = self.pixels[1][2] = self.pixels[1][1] = self.pixels[2][1] = color

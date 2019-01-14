#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan  3 11:41:49 2019

@author: stefan
"""
import matplotlib
import matplotlib.pyplot as plt
import numpy as np

class statistics():
    
    def __init__(self):
        self.linesList = [0]*1
        self.tetrominosList = [0]*1
        self.fig, self.ax = plt.subplots()
        self.fig.show()
    
    def plotStatistics(self, lines, tetrominos):
        self.linesList = np.append(self.linesList, lines/tetrominos)
        self.tetrominosList = np.append(self.tetrominosList, tetrominos)
        #print(self.linesList)
        #print(self.tetrominosList)
        
        self.ax.plot(self.tetrominosList, self.linesList)
        self.ax.set(xlabel='Total Tetrominos', ylabel='Reihen/Tetrominos',title='Güte der Strategie')
        self.ax.grid()
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
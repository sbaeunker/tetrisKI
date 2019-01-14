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
        self.rateList = [0]*1
        self.fig, self.ax = plt.subplots()
        self.fig.show()
    
    def plotStatistics(self, lines, tetrominos):
        self.linesList = np.append(self.linesList, lines)
        self.tetrominosList = np.append(self.tetrominosList, tetrominos)
        self.rateList = np.append(self.rateList, (self.linesList[-1]-self.linesList[-2])/(self.tetrominosList[-1]-self.tetrominosList[-2]))
        #print(self.linesList)
        #print(self.tetrominosList)
        if(self.rateList.shape[0]>2):
            self.ax.plot(self.tetrominosList[0:self.rateList.shape[0]],self.rateList )
            self.ax.set(xlabel='Total Tetrominos', ylabel='Reihen/Tetrominos',title='Güte der Strategie')
            self.ax.grid()
            self.fig.canvas.draw()
            self.fig.canvas.flush_events()
            
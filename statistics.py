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
        
    
    def plotStatistics(self, lines, tetrominos):
        self.linesList = np.append(self.linesList, lines)
        self.tetrominosList = np.append(self.tetrominosList, tetrominos)
        print(self.linesList)
        print(self.tetrominosList)
        fig, ax = plt.subplots()
        ax.plot(self.tetrominosList, self.linesList)
        ax.set(xlabel='Total Tetrominos', ylabel='Reihen',title='Reihen über Anzahl platzierte Steine')
        ax.grid()
        plt.show()
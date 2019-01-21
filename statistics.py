#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan  3 11:41:49 2019

@author: stefan
"""
#import time
import datetime
import matplotlib.pyplot as plt
import numpy as np

class statistics():
    
    def __init__(self, agent):
        self.filename = datetime.datetime.now().strftime("%m.%d,%H:%M")+"statistik.csv"
        self.agent = agent
        self.saveFreq = 3
        self.saveCycle = 0
        self.linesList = [0]*1
        self.tetrominosList = [0]*1
        self.rateList = [0]*1
        #self.timesList = [datetime.datetime.now().strftime("%H:%M")]
        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1)
        self.fig.show()
        
    
    def plotStatistics(self, lines, tetrominos):
        
        if(len(self.linesList)==1 and self.saveCycle==0):
             self.linesList[0]= lines
             self.tetrominosList[0]= tetrominos
        else:
            self.linesList = np.append(self.linesList, lines)
            self.tetrominosList = np.append(self.tetrominosList, tetrominos)
            #self.timesList = np.append(self.timesList, datetime.datetime.now().strftime("%H:%M"))
            self.ax1.plot(self.tetrominosList,self.linesList)
            self.ax1.set(xlabel='Total Tetrominos', ylabel='Reihen',title='Reihen über Tetrominos')
            self.ax1.grid()
            if(len(self.rateList)== 1 and self.saveCycle<=1):
                self.rateList[0] =(self.linesList[-1]-self.linesList[-2])/(self.tetrominosList[-1]-self.tetrominosList[-2])
                with open(self.filename[:-13]+"kerasModel.txt",'w') as fh:
                    # Pass the file handle in as a lambda function to make it callable
                    self.agent.Q.summary(print_fn=lambda x: fh.write(x + '\n'))
            else:
                self.rateList = np.append(self.rateList, (self.linesList[-1]-self.linesList[-2])/(self.tetrominosList[-1]-self.tetrominosList[-2]))
                self.ax2.plot(self.tetrominosList[0:self.rateList.shape[0]],self.rateList )
                self.ax2.set(xlabel='Total Tetrominos', ylabel='Reihen/Tetrominos',title='Güte der Strategie')
                self.ax2.grid()

        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
        self.saveCycle+=1 
        if(self.saveCycle%self.saveFreq==0):
            self.saveData()
            self.saveCycle = 0
            
    def saveData(self):
        data = np.transpose(np.vstack([self.linesList,self.tetrominosList,np.append(self.rateList,0)]))
        header = "Alpha:"+str(self.agent.alpha)+" Gamma:"+str(self.agent.gamma)+" Tau:"+ str(self.agent.tau)+" updateF:"+str(self.agent.updateFeq)+" gameSize:"+str(self.agent.gameSize) +"\nlines,Tetrominos,dli/dTetro"
        np.savetxt(self.filename,data,delimiter=",",header= header)
        
        
        
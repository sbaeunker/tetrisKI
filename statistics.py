#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
import matplotlib.pyplot as plt
import numpy as np

########### Zeichnet die Plots während der Agent lernt und speichert die Plotdaten als CSV ###############

class statistics():
    
    def __init__(self, agent):
        self.filename = datetime.datetime.now().strftime("%m.%d,%H:%M")+"statistik.csv"
        self.agent = agent
        self.saveFreq = 3
        self.saveCycle = 0
        self.linesList = [0]*1
        self.tetrominosList = [0]*1
        self.rateList = [0]*1
        self.gameList = [0]*1
        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1)
        self.fig.show()
        
    
    def plotStatistics(self, lines, tetrominos, games):
        
        if(len(self.linesList)==1 and self.saveCycle==0):
             
             self.linesList[0]= lines
             self.tetrominosList[0]= tetrominos
        else:
            self.linesList = np.append(self.linesList, lines)
            self.tetrominosList = np.append(self.tetrominosList, tetrominos)            
            if(len(self.rateList)== 1 and self.saveCycle<=1):
                self.rateList[0] =(self.linesList[-1]-self.linesList[-2])/(self.tetrominosList[-1]-self.tetrominosList[-2])
                self.gameList[0] =(self.linesList[-1]-self.linesList[-2])/(games-self.prevGames)
                with open(self.filename[:-13]+"kerasModel.txt",'w') as fh:# Beim ersten loop das verwendete NN Modell als text abspeichern
                    # Pass the file handle in as a lambda function to make it callable
                    self.agent.Q.summary(print_fn=lambda x: fh.write(x + '\n'))
            else:
                self.rateList = np.append(self.rateList, (self.linesList[-1]-self.linesList[-2])/(self.tetrominosList[-1]-self.tetrominosList[-2]))
                self.gameList = np.append(self.gameList, (self.linesList[-1]-self.linesList[-2])/(games-self.prevGames))
                self.ax1.plot(self.tetrominosList[0:self.rateList.shape[0]],self.gameList)
                self.ax1.set(xlabel='Total Tetrominos', ylabel='Reihen',title='Reihen pro Spiel')
                self.ax1.grid()
                self.ax2.plot(self.tetrominosList[0:self.rateList.shape[0]],self.rateList )
                self.ax2.set(xlabel='Total Tetrominos', ylabel='Reihen/Tetrominos',title='Güte der Strategie')
                self.ax2.grid()
        self.prevGames = games
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
        self.saveCycle+=1 
        if(self.saveCycle%self.saveFreq==0):
            self.saveData()
            self.saveCycle = 0
            
    def saveData(self):
        data = np.transpose(np.vstack([self.linesList,self.tetrominosList,np.append(self.rateList,0),np.append(self.gameList,0)]))
        header = "Alpha:"+str(self.agent.alpha)+" Gamma:"+str(self.agent.gamma)+" Tau:"+ str(self.agent.tau)+" updateF:"+str(self.agent.updateFeq)+" gameSize:"+str(self.agent.gameSize) +"\nlines,Tetrominos,dli/dTetro"
        np.savetxt(self.filename,data,delimiter=",",header= header)
        
        
        

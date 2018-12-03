
import numpy as np
from QLearningEnv import boxEnvironment, robotAgent
import keras
from keras.models import Sequential
from keras.layers import Dense
from keras.reqularizers import l2

class tetrisAgent:
    
    def __init__(self, tau=1, memoryMax=1000000, alpha=0.5, gamma=0.7, badMemory=3000):
        self.alpha = alpha
        self.tau = tau
        self.memoryMax = memoryMax
        self.gamma = gamma
        self.badMemory = badMemory
    
    #Wählt die nächste Aktion und gibt den Reward zurück
    def chooseAction(self, gamepad, tetromino, nextTetromino):
        
        
    def __calcReward(self, gamepad):
    
    

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
    
    def __getActionSpaceSize(self, spielfeld, tetromino):
         switch(tetromin.kind){#return Anzahl der Möglichkeiten
                case 1:#umgekehrtes L
                    return 34;#8+8+9+9
                    break;
                case 2:#L
                    return 34;#8+8+9+9
                    break;
                case 3:#Z
                    return 17;#8+9
                    break;
                case 4:#S
                    return 17;#8+9
                    break;
                case 5:#T
                    return 34;#8+8+9+9
                    break;
                case 6:#O
                    return 9;#9
                    break;
                case 7:#I
                    return 17; #10+7
                    break;
                }
        
    def __getActionSpace(self, spielfeld, tetromino):
        size = __getActionSpaceSize(spielfeld, tetromino)
        outputSpielfeld = [spielfeld]*size;
        for i in range(size):
            
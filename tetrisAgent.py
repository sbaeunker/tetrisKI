
import numpy as np
#from QLearningEnv import boxEnvironment, robotAgent
#import keras
#from keras.models import Sequential
#from keras.layers import Dense
#from keras.reqularizers import l2

class tetrisAgent:
    
    def __init__(self, maxContourDiff, gameWidth, actionAmount, alpha=0.5, gamma=0.7, vareps=0.1):
        self.alpha = alpha
        self.gamma = gamma
        self.vareps = vareps
        self.statusSize = gameWidth-1
        self.actionAmount = actionAmount
        self.base = maxContourDiff*2+1

        #Anzahl aller Möglichen Konturen
        self.contourPoss = self.base**self.statusSize
        #Q-Werte-Array
        self.hatQ = np.zeros((self.contourPoss,actionAmount))

    def statusToQHatIdx(self,status):
        res = 0
        for i in range(self.statusSize):
            res = res + status[i]*(self.base**i)
        return res
    
    #Wählt die nächste Aktion und gibt den Reward zurück
    def chooseAction(self, contour):
        rand = np.random.rand(1)

        if rand < self.vareps:
            a = np.random.randint(self.actionAmount)
        else:
            idx = statusToQHatIdx(contour)
            localQ = self.hatQ[idx,:]
            a = np.argmax(localQ)
        return a

    def learn(self,contourBefore,contourAfter, revard, lastAction):
        localQ = self.hatQ[statusToQHatIdx(contourAfter),:]
        self.hatQ[statusToQHatIdx(contourBefore),lastAction] = r + self.gamma * np.max(localQs)
        a = np.argmax(localQ)

    def getRevard(self, deletedLines, contourBefore, contourAfter):
        revard = -1
        revard = revard + deletedLines * 1000
        revard = revard + ( np.sum(np.absolute(contourBefore)) - np.sum(np.absolute(contourAfter)))
        return revard
        
    #def __calcReward(self, gamepad):
    
    # def __getActionSpaceSize(self, spielfeld, tetromino):
    #      switch(tetromin.kind){#return Anzahl der Möglichkeiten
    #             case 1:#umgekehrtes L
    #                 return 34;#8+8+9+9
    #                 break;
    #             case 2:#L
    #                 return 34;#8+8+9+9
    #                 break;
    #             case 3:#Z
    #                 return 17;#8+9
    #                 break;
    #             case 4:#S
    #                 return 17;#8+9
    #                 break;
    #             case 5:#T
    #                 return 34;#8+8+9+9
    #                 break;
    #             case 6:#O
    #                 return 9;#9
    #                 break;
    #             case 7:#I
    #                 return 17; #10+7
    #                 break;
    #             }
        
    # def __getActionSpace(self, spielfeld, tetromino):
    #     size = __getActionSpaceSize(spielfeld, tetromino)
    #     outputSpielfeld = [spielfeld]*size;
    #     for i in range(size):
            
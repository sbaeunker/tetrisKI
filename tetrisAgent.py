
import numpy as np
#from QLearningEnv import boxEnvironment, robotAgent
#import keras
#from keras.models import Sequential
#from keras.layers import Dense
#from keras.reqularizers import l2

class tetrisAgent:
    
    def __init__(self, maxContourDiff, amountTetrominos, gameWidth, actionAmount, alpha=0.5, gamma=0.7, vareps=0.1):
        self.alpha = alpha
        self.gamma = gamma
        self.vareps = vareps
        self.statusSize = gameWidth-1
        self.actionAmount = actionAmount
        self.base = maxContourDiff*2+1
        self.amountTetrominos = amountTetrominos

        #Anzahl aller Möglichen Konturen
        self.contourPoss = (self.base**self.statusSize)*amountTetrominos
        #Q-Werte-Array
        self.hatQ = np.zeros((self.contourPoss,actionAmount))

    def statusToQHatIdx(self,status):
        res = 0
        for i in range(self.statusSize):
            res = res + status[i]*(self.base**i)
        return res
    
    #Wählt die nächste Aktion und gibt den Reward zurück
    def chooseAction(self, contour, tetrominoKind):
        rand = np.random.rand(1)

        if rand < self.vareps:
            a = np.random.randint(self.actionAmount)
        else:
            idx = self.statusToQHatIdx(contour)+tetrominoKind-1
            localQ = self.hatQ[idx,:]
            a = np.argmax(localQ)
        return a

    def learn(self,contourBefore,contourAfter, reward, lastAction, tetrominoKind):
        localQ = self.hatQ[self.statusToQHatIdx(contourAfter)+tetrominoKind,:]
        self.hatQ[self.statusToQHatIdx(contourBefore)+tetrominoKind,lastAction] = reward + self.gamma * np.max(localQ)
        #a = np.argmax(localQ)
        

    def getReward(self, deletedLines, contourBefore, contourAfter):
        reward = -1
        reward = reward + deletedLines * 1000
        reward = reward + 10*( np.sum(np.absolute(contourBefore)) - np.sum(np.absolute(contourAfter)))
        return reward
        
    #def __calcReward(self, gamepad):
    
    
        
    
        
        
        # xKoordinaten von den unteren blöcken des Tetromino
        
        
   #     if(tetromino.kind == 1): #umgekehrtes L
	#		if(actionIndex>34):#nur 34 Möglichkeiten 8+8+9+9
	#			return -1 
	#		if(actionIndex<=8): 
	#			tetrominoPositions = np.array([[0,1,1,1][0,0,1,2]])
	#			return
	#		else if(actionIndex<=16):
	#			tetrominoPositions = np.array([[0,0,0,1][0,1,2,2]])
	#			return
	#		else if(actionIndex<=25):
	#			tetrominoPositions = np.array([[0,1,1,1][0,1,2,3]])
	#			return
	#		else if(actionIndex<=34):
	#			tetrominoPositions = np.array([[0,1,1,1][0,1,2,3]])
	#			return
	#	else if(tetromino.kind == 2): #L
	#		if(actionIndex>34):#nur 34 Möglichkeiten 8+8+9+9
	#			return -1 
	#	else if(tetromino.kind == 3): #Z
	#		if(actionIndex>34):#nur 34 Möglichkeiten 8+9
	#			return -1 
	#	else if(tetromino.kind == 4): #S
	#		if(actionIndex>34):#nur 34 Möglichkeiten 8+9
	#			return -1 
	#	else if(tetromino.kind == 5): #T
	#		if(actionIndex>34):#nur 34 Möglichkeiten 8+8+9+9
	#			return -1 
	#	else if(tetromino.kind == 6): #O
	#		if(actionIndex>34):#nur 34 Möglichkeiten 9
	#			return -1 
	#	else if(tetromino.kind == 7): #I
	#		if(actionIndex>34):#nur 34 Möglichkeiten 10+7
	#			return -1 		       
            

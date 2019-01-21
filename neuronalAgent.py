import numpy as np
#from QLearningEnv import boxEnvironment, robotAgent
import keras
from keras.models import Sequential
from keras.layers import Dense
from keras.regularizers import l2
from keras.models import load_model

class neuronalAgent():

    #Konstruktor der Klasse
    #Initialisiert alle Arrays und sonstigne Dinge die benötigt werden
    def __init__(self, tau=1, actionAmount=18, memoryMax=1000000, alpha=0.3, gamma=0.5, updateFeq=500, badMemory = 3000, gameSize = 6):
        # Gewicht, wie stark die alte Q-Aproximation bei der weitern Annäherung berücksichtigt wird (bestimmt Änderungsrate von Aproximiertem Q)
        # [0,1]; 0=> Nur der alte Wert gilt (vollkommen sinnlos); 1=> nur die neuberechnete Aproximation wird berücksichtigt
        self.alpha = alpha
        # Gewicht, wie stark zukünfige Belohnungen gewichtet werden
        # [0,1); 0=> Nur der direkte Reward zählt; gegen 1 => nahezu alle zukünfigen Rewards werden berücksichtigt
        self.gamma = gamma
        
        self.tau = tau
        self.memoryMax = memoryMax
        self.updateFeq = updateFeq
        self.badMemory = badMemory
        self.actionAmount = actionAmount
        # Liste aller möglichen Aktionen
        self.a = np.array(range(0,actionAmount))
        # Counter und aktueller Gedächnisindex für Gedächnisarrays (siehe initMemory)
        self.memoryCounter = -1         # Zählvariable für die Speicherwerte/das Gedächnis
        # In der ersten Phase ist die Q-Funktion noch BLA und daher gibt es eine initPhase in der die Aktionen vorgeschrieben werden
        self.initPhase = True
        self.gameSize = gameSize
        self.initMemory(gameSize)

    #Initialisiert die Speicherwert/Gedächniswerte
    def initMemory(self, number):
        #Speicherwerte für Q-Funktions-Approximation
        #(s,r,a,s') wobei s' durch den nächsten Eintrag gespeichert wird, da dieser sonst doppelt vorkommen würde
        self.memoryStates = np.inf*np.ones( (self.memoryMax, number) )
        self.memoryActions = np.inf*np.ones(self.memoryMax)
        self.rewards = np.zeros(self.memoryMax)
        

    def saveNetwork(self, filename):
        self.Q.save(filename + ".model.h5")
        self.Q.save_weights(filename + '.weights.h5')
    
    def saveData( self, filename, size):
        if size == None:
            size = min(self.me,self.memoryActions.shape[0],self.rewards.shape[0])
        else:
            size = min(size,self.memoryMax)
        data = np.transpose(np.vstack((np.transpose(self.memoryStates[0:size,:]),self.memoryActions[0:size],self.rewards[0:size])))
        header = ""
        for i in range(self.memoryStates[self.memoryCounter,:].shape[0]):
            header+= "states" + str(i) +","
        header+="Action,Reward"
        np.savetxt(filename+".csv",data,delimiter=",",header= header)
    
    def loadNetwork(self, filename):
        try:
            del self.Q
            
        except:
            print("INFO: Neuronalnet is not initialisized")
            
        self._initQ()
        try:
            self.Q.load_weights(filename+".weights.h5")
        except:
            print("ERROR: no neuronal network file found!")

    def loadData(self, filename):
        data = np.loadtxt(filename+".csv",delimiter=",",skiprows=1)
        self.memoryCounter = data.shape[0]-1
        self.memoryActions[0:self.memoryCounter+1] = np.transpose(data[:,6])       
        self.memoryStates[0:self.memoryCounter+1,:] = data[:,0:self.gameSize]
        self.rewards[0:self.memoryCounter+1] = np.transpose(data[:,7])
    
    def calcReward(self, deletedLines, spielfeldVorher, spielfeldNachher):       
        spielfeldVorher = spielfeldVorher !=0 # y Koordinaten != 0
        spielfeldNachher = spielfeldNachher !=0
        
        #print(spielfeldVorher)
        #print(spielfeldNachher)
        contourVorher = np.zeros((spielfeldVorher.shape[0],1), dtype=int)
        contourNachher = np.zeros((spielfeldNachher.shape[0],1), dtype=int)
        holesVorher = 0
        holesNachher = 0
        
        for col in range(spielfeldVorher.shape[0]): # maximal Anzal SpielfeldBreite loops
            #check if row is empty
            if np.where(spielfeldVorher[:][col])[:][0].size == 0:
                contourVorher[col][0] = 0
            else:
                contourVorher[col][0] = spielfeldVorher.shape[1] - min(np.where(spielfeldVorher[:][col])[:][0])
                # find holes sucht nach aufeinanderfolgenden 1 und 0
                #print(spielfeldVorher[col,0:(spielfeldVorher.shape[1]-1)])
                #print(spielfeldVorher[col,1:(spielfeldVorher.shape[1])])
                holesVorher += np.count_nonzero(np.logical_and(spielfeldVorher[col,0:(spielfeldVorher.shape[1]-1)] == 1 , spielfeldVorher[col,1:(spielfeldVorher.shape[1])] == 0))
            
        for col in range(spielfeldNachher.shape[0]): 
            #check if row is empty
            if np.where(spielfeldNachher[:][col])[:][0].size == 0:
                contourNachher[col][0] = 0
            else:
                contourNachher[col][0] = spielfeldNachher.shape[1] - min(np.where(spielfeldNachher[:][col])[:][0])
                # find holes
                holesNachher += np.count_nonzero(np.logical_and(spielfeldNachher[col,0:spielfeldNachher.shape[1]-1]==1,spielfeldNachher[col,1:spielfeldNachher.shape[1]] == 0))
        #print("contourVoher",contourVorher)
        #print("contourNachher",contourNachher)
        
        heightDiff= max(contourNachher[:])-max(contourVorher[:])[0]
        holesDiff =  holesNachher - holesVorher
        #print("holes",holesDiff)
        #print("heightdiff",heightDiff)
        self.rewards[self.memoryCounter]  = -1
        self.rewards[self.memoryCounter] += deletedLines*150
        self.rewards[self.memoryCounter]  -= 50 * holesDiff
        if(holesDiff == 0):
            self.rewards[self.memoryCounter] += 100
        # nicht für löcher bestrafen da diese nicht immer sichtbar sind
        if(heightDiff > 0):#kleine Strafe bei größerer höhe
            self.rewards[self.memoryCounter] -=(max(contourVorher[:])[0]- min(contourVorher[:])[0])*heightDiff #soll türmchen verhindern
        else: #Belohnung gleicher höhe // kleinere höhe nur beim löschen der Line möglich
            self.rewards[self.memoryCounter] += 50  
        
        #print(self.rewards[self.memoryCounter])
        
    def _initQ(self):
        # np.hstack: Stack arrays in sequence horizontally (column wise)
        # Legt das Wertetupel (Status, Aktion) an
        xTrain = np.hstack( (self.memoryStates[0:self.memoryCounter,:],self.memoryActions[0:self.memoryCounter,None]) )
        self.Q = Sequential()

        self.Q.add(Dense(256, input_dim=xTrain.shape[1], activation='relu', kernel_regularizer=l2(0.0001)))
        self.Q.add(Dense(128, activation='relu', kernel_regularizer=l2(0.0001)))
        self.Q.add(Dense(64, activation='relu', kernel_regularizer=l2(0.0001)))
        self.Q.add(Dense(1, activation='linear'))

        clist = [keras.callbacks.EarlyStopping(monitor='loss',patience=5,verbose=0,mode='auto')]

        self.Q.compile(loss ='mean_squared_error', optimizer='adam')
        self.Q.fit(xTrain, self.alpha*self.rewards[0:xTrain.shape[0]], epochs=50, callbacks=clist, batch_size=5, verbose=False)
    
    def _updateQ(self):
        learnSet = np.arange(0,self.memoryCounter-1)
        index1 = np.flatnonzero(self.rewards[learnSet]<-0.9)    #   Suche alle Rewards kleiner als konst. Wert; neuster Reward wird nicht beachtet
        #Überprüfe ob zu viele Werte für den miniBatch vorliegen. Wenn ja suche zufällig welche raus
        if index1.shape[0] > self.badMemory:             
            index = np.random.choice(index1.shape[0], self.badMemory, replace=False)
            index1 = index1[index]
        #Nimm noch mehr Werte für den Batch dazu
        samplesleft = min(index1.shape[0]*5,self.memoryCounter-index1.shape[0]-1)
        index2 = np.random.choice(self.memoryCounter-1, samplesleft, replace=False)
        #Beide Wertearrays zusammenhängen
        learnSet = np.hstack( (index1[None,:], index2[None,:]) )
        learnSet = np.reshape(learnSet, learnSet.shape[1])
        # Wertetupel (State, Action)
        x = np.hstack( (self.memoryStates[learnSet,: ], self.memoryActions[learnSet,None]))

        #Update NeuronalNetwork
        qAlt = np.squeeze(self.Q.predict(x))
        qChoose = np.zeros( (qAlt.shape[0], len(self.a)) )
        for i in range(len(self.a)):
            a = self.a[i]*np.ones_like(self.memoryActions[learnSet,None])
            xTemp = np.hstack( (self.memoryStates[learnSet+1,:],a))
            qChoose[:,i] = np.squeeze(self.Q.predict(xTemp))
        qMax = np.max(qChoose, axis=1)
        r = self.rewards[learnSet]
        qNeu = (1-self.alpha)*qAlt + self.alpha*(r + self.gamma*qMax)
        self.Q.fit(x, qNeu, epochs=3, batch_size=5, verbose=False)

    def _softmax(self,qA):
        return np.exp(qA/self.tau) / np.sum(np.exp(qA/self.tau))
    
    def chooseAction(self,qA):
        toChoose = np.arange(0,len(qA))
        pW = self._softmax(qA)
        if np.any(np.isnan(pW)) or np.any(np.isinf(pW)):
            choosenA = np.random.randint(0,len(qA))
        else:
            choosenA = np.random.choice(toChoose, replace=False, p=pW)
        return(choosenA)

    def learn(self,status):
        self.memoryCounter +=1
        if self.memoryCounter%self.updateFeq == 0 and not self.initPhase:
            self._updateQ()
        if self.memoryCounter > min(500,self.memoryMax-1) and self.initPhase:
            self.initPhase = False
            self._initQ()
            self._updateQ()
        
        # Speicher aktuellen Status
        self.memoryStates[self.memoryCounter,:] = status
        
        if self.initPhase:
            self.initPhase = True
            w =  np.random.randint(self.actionAmount)
        else:
            qA = np.zeros_like(self.a)
            j = self.memoryStates[self.memoryCounter,:].shape[0]
            x = np.zeros( (1, j+1) )
            x[0,0:j] = self.memoryStates[self.memoryCounter,:]

            for i in range(len(self.a)):
                x[0,self.memoryStates[self.memoryCounter,:].shape[0]] = self.a[i]
                qA[i] = self.Q.predict(x)[0]
            ca = self.chooseAction(qA)
            w = self.a[ca]

        # Speicher aktuelle Aktion
        self.memoryActions[self.memoryCounter] = w
        return(w)

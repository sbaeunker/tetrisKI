import numpy as np
import keras
from keras.models import Sequential
from keras.layers import Dense
from keras.regularizers import l2
#from heapq import nlargest
#from keras.models import load_model
import os

class neuronalAgent():

    #Konstruktor der Klasse
    #Initialisiert alle Arrays und sonstigne Dinge die benötigt werden
    def __init__(self, gameSize = 6, tau=5, memoryMax=1000000, alpha=0.3, gamma=0.6, updateFeq=500, badMemory = 5000):
        # Gewicht, wie stark die alte Q-Aproximation bei der weitern Annäherung berücksichtigt wird (bestimmt Änderungsrate von Aproximiertem Q)
        # [0,1]; 0=> Nur der alte Wert gilt (vollkommen sinnlos); 1=> nur die neuberechnete Aproximation wird berücksichtigt
        self.alpha = alpha
        # Gewicht, wie stark zukünfige Belohnungen gewichtet werden
        # [0,1); 0=> Nur der direkte Reward zählt; gegen 1 => nahezu alle zukünfigen Rewards werden berücksichtigt
        self.gamma = gamma
        #Nur CPU benutzen da deutlich schneller bei verwendetem kleinen Netz
        os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"   
        os.environ["CUDA_VISIBLE_DEVICES"] = ""
        
        self.stopLearning = False # flag zum abstellen der Exploration und Q-Funktion update
        self.overwriteMemory = False # flag zum markieren des Speicherüberlaufs
        
        
        self.tau = tau # aggressivität der Explorations Strategie
        self.memoryMax = memoryMax # maximale Anzahl von Datensätzen mit Status, Aktion, Reward
        self.updateFeq = updateFeq # so viele Tetrominos werden platziert bevor der Agent erneut lernt
        self.badMemory = badMemory # grösse des durch auswahl gebildeten Batches
        self.actionAmount = 4*gameSize -6 # Anzahl der möglichen Aktionen pro Tetromino
        
        
        # Liste aller möglichen Aktionen
        self.a = np.array(range(0,self.actionAmount))
        # Counter und aktueller Gedächnisindex für Gedächnisarrays (siehe initMemory)
        self.memoryCounter = -1         # Zählvariable für die Speicherwerte/das Gedächnis
        # In der ersten Phase ist die Q-Funktion noch BLA und daher gibt es eine initPhase in der die Aktionen vorgeschrieben werden
        self.initPhase = True
        self.gameSize = gameSize
        self.initMemory(gameSize+1) #gameSize -1 für Kontur und +1 für Tetromino kind =0 

    #Initialisiert die Speicherwert/Gedächniswerte
    def initMemory(self, number):
        #Speicherwerte für Q-Funktions-Approximation
        #(s,r,a,s') wobei s' durch den nächsten Eintrag gespeichert wird, da dieser sonst doppelt vorkommen würde
        self.memoryStates = np.inf*np.ones( (self.memoryMax, number) )
        self.memoryActions = np.inf*np.ones(self.memoryMax)
        self.rewards = np.zeros(self.memoryMax)
        

    def saveNetwork(self, filename):
        #Speichern des Models und der Gewichte des Neuronalen Netzes ermöglicht späteres Laden
        self.Q.save(filename + ".model.h5")
        self.Q.save_weights(filename + '.weights.h5')
        print("Neuronal Network saved")
    
    def saveData( self, filename, size):
        #Speichert die aktuell im Speicher gehaltenen Datensätze mit Aktion, Reward und Status als csv.
        #Ermöglicht späteres Laden und 
        if size == None:
            size = min(self.me,self.memoryActions.shape[0],self.rewards.shape[0])
        else:
            size = min(size,self.memoryMax)
        data = np.transpose(np.vstack((np.transpose(self.memoryStates[0:size,:]),self.memoryActions[0:size],self.rewards[0:size])))
        header = ""
        for i in range(self.memoryStates[self.memoryCounter,:].shape[0]):#Comma delimited CSV mit beschreibenden Header
            header+= "states" + str(i) +","
        header+="Action,Reward"
        np.savetxt(filename+".csv",data,delimiter=",",header= header)
        print("Data saved")
    
    def loadNetwork(self, filename):
        #laden der Netzwerk Gewichte in ein neues neuronales Netzwerk
        try:
            del self.Q            
        except:
            print("INFO: Neuronalnet was not previously initialisized")
        self.Q = Sequential()
        self.Q.add(Dense(256, input_dim=self.gameSize+2, activation='relu', kernel_regularizer=l2(0.0001)))
        self.Q.add(Dense(128, activation='relu', kernel_regularizer=l2(0.0001)))
        self.Q.add(Dense(64, activation='relu', kernel_regularizer=l2(0.0001)))
        self.Q.add(Dense(1, activation='linear'))

        clist = [keras.callbacks.EarlyStopping(monitor='loss',patience=5,verbose=0,mode='auto')]

        self.Q.compile(loss ='mean_squared_error', optimizer='adam')
        self.initPhase = False # netzwerk muss nicht mehr mit zufalls Daten initialisiert werden sondern kann direkt mit softmax exploration starten
        
        try:
            self.Q.load_weights(filename+".weights.h5")
            print("Neuronal Network loaded")
        except:
            print("\nERROR: no neuronal network file found named " + filename+".weights.h5 !\n")
        
        

    def loadData(self, filename):
        #Lädt die in der CSV abgespeicherten Spiel Daten mit Aktion Reward und Status
        data = np.loadtxt(filename+".csv",delimiter=",",skiprows=1)
        self.memoryCounter = data.shape[0]-1
        self.memoryActions[0:self.memoryCounter+1] = np.transpose(data[:,7])       
        self.memoryStates[0:self.memoryCounter+1,:] = data[:,0:self.gameSize+1]
        self.rewards[0:self.memoryCounter+1] = np.transpose(data[:,7])
        print("Data loaded")

    
    def calcReward(self, deletedLines, spielfeldVorher, spielfeldNachher):
        #die Rewardfunktion erhält ehr informationen als der Agent, nämlich das gesamte Spielfeld
        spielfeldVorher = spielfeldVorher !=0 # unwandlung in boolsches array, eliminiert informationen über tetrominokind
        spielfeldNachher = spielfeldNachher !=0
        
        
        #Variablen speichern die gestapelte Höhe pro Spalte des Spielfelds und sind damit eine andere Kontur, als die im Status des Agenten
        contourVorher = np.zeros((spielfeldVorher.shape[0],1), dtype=int)
        contourNachher = np.zeros((spielfeldNachher.shape[0],1), dtype=int)
        holesVorher = 0
        holesNachher = 0
        
        for col in range(spielfeldVorher.shape[0]): # wenige loops : maximal Anzahl SpielfeldBreite z.B. 10           
            #spaltenweises bilden der höhe pro Spalte und suchen nach Löchern im alten Spielfeld
            if np.where(spielfeldVorher[:][col])[:][0].size == 0:#check if row is empty
                contourVorher[col][0] = 0
            else:
                contourVorher[col][0] = spielfeldVorher.shape[1] - min(np.where(spielfeldVorher[:][col])[:][0])
                #find holes
                holesVorher += np.count_nonzero(np.logical_and(spielfeldVorher[col,0:(spielfeldVorher.shape[1]-1)] == 1 , spielfeldVorher[col,1:(spielfeldVorher.shape[1])] == 0))
            
        for col in range(spielfeldNachher.shape[0]): 
            #spaltenweises bilden der höhe pro Spalte und suchen nach Löchern im alten Spielfeld
            if np.where(spielfeldNachher[:][col])[:][0].size == 0:#check if row is empty
                contourNachher[col][0] = 0
            else:
                contourNachher[col][0] = spielfeldNachher.shape[1] - min(np.where(spielfeldNachher[:][col])[:][0])
                # find holes
                holesNachher += np.count_nonzero(np.logical_and(spielfeldNachher[col,0:spielfeldNachher.shape[1]-1]==1,spielfeldNachher[col,1:spielfeldNachher.shape[1]] == 0))
        
        heightDiff= max(contourNachher[:])-max(contourVorher[:])[0] #Array mit Höhenänderung pro Spalte
        holesDiff =  holesNachher - holesVorher # Anzahl der neu hinzugekommenen Löcher
        self.rewards[self.memoryCounter]  = -1
        self.rewards[self.memoryCounter] += deletedLines*150
        self.rewards[self.memoryCounter]  -= 50 * holesDiff
        if(holesDiff == 0):
            self.rewards[self.memoryCounter] += 100#große Belohnung falls weniger Löcher als vorher
        if(heightDiff > 0):#kleine Strafe bei größerer höhe
            self.rewards[self.memoryCounter] -=5*max(contourNachher[:])[0]*heightDiff #soll türmchen verhindern
        else: #Belohnung gleicher höhe // kleinere höhe nur beim löschen der Reihe möglich
            self.rewards[self.memoryCounter] += 50 

        
    def _initQ(self):
        # np.hstack: Stack arrays in sequence horizontally (column wise)
        # Legt das Wertetupel (Status, Aktion) an
        xTrain = np.hstack( (self.memoryStates[max(self.memoryCounter-self.updateFeq,0):self.memoryCounter,:],self.memoryActions[max(self.memoryCounter-self.updateFeq,0):self.memoryCounter,None]) )
        self.Q = Sequential()

        self.Q.add(Dense(256, input_dim=xTrain.shape[1], activation='relu', kernel_regularizer=l2(0.0001)))
        self.Q.add(Dense(128, activation='relu', kernel_regularizer=l2(0.0001)))
        self.Q.add(Dense(64, activation='relu', kernel_regularizer=l2(0.0001)))
        self.Q.add(Dense(1, activation='linear'))

        clist = [keras.callbacks.EarlyStopping(monitor='loss',patience=5,verbose=0,mode='auto')]

        self.Q.compile(loss ='mean_squared_error', optimizer='adam')
        self.Q.fit(xTrain, self.alpha*self.rewards[0:xTrain.shape[0]], epochs=50, callbacks=clist, batch_size=5, verbose=False)
    
    def _updateQ(self):

        if not self.overwriteMemory: #falls Speicher bereits übergelaufen aus gesamten Daten den Batch zusammen stellen
            setSize = self.memoryCounter-1 #memory Counter index wird weiter unten immer gelöscht weil ja learnSet+1 predicted werden muss 
            learnSet= np.arange(0,setSize)
        else:
            setSize = self.memoryMax-1 #memoryCounter auch nicht gewählt werden können, da die Si und Si+1 nicht zueinander passen passiert aber praktisch nie
            learnSet = np.delete(np.arange(0,setSize),self.memoryCounter-2)# überlauf element löschen, auch bei überlauf nötig
        
        index1 = np.flatnonzero(np.logical_or(self.rewards[learnSet]<0.5*min(self.rewards[learnSet]) , self.rewards[learnSet] > 0.5* max(self.rewards[learnSet])))    #   Suche alle Rewards kleiner als konst. Wert; neuster Reward wird nicht beachtet
        #index1 = np.flatnonzero(self.rewards[learnSet]<0)
        #index1 = np.array(nlargest(int(self.badMemory/2),range(len(self.rewards[learnSet])),self.rewards.take))
        #index3 = np.array(nlargest(int(self.badMemory/2),range(len(self.rewards[learnSet])),(-1*self.rewards).take))
        

        #Überprüfe ob zu viele Werte für den miniBatch vorliegen. Wenn ja suche zufällig welche raus
        if index1.shape[0] > self.badMemory:             
            index = np.random.choice(index1.shape[0], self.badMemory, replace=False)
            index1 = index1[index]
        #Nimm noch mehr Werte für den Batch dazu
        index3=np.arange(self.memoryCounter-self.updateFeq,self.memoryCounter-1) # alle neu hinzugekommenen Daten
        index1 = np.hstack( (index1, index3) )
        
        samplesleft = min(int(index1.shape[0]*3),self.memoryCounter-index1.shape[0]-1)
        
        index2 = np.random.choice(setSize, samplesleft, replace=False) #Zufallsdaten
        #Beide Wertearrays zusammenhängen
        learnSet = np.hstack( (index1[None,:], index2[None,:]) )
        learnSet = np.reshape(learnSet, learnSet.shape[1])
        # Wertetupel (State, Action)
        x = np.hstack( (self.memoryStates[learnSet,: ], self.memoryActions[learnSet,None])) # Eingangswerte für das NN Training

        #Update NeuronalNetwork
        qAlt = np.squeeze(self.Q.predict(x)) #Q funktion für Qi
        qChoose = np.zeros( (qAlt.shape[0], len(self.a)) )
        for i in range(len(self.a)):
            a = self.a[i]*np.ones_like(self.memoryActions[learnSet,None])
            xTemp = np.hstack( (self.memoryStates[learnSet+1,:],a))
            qChoose[:,i] = np.squeeze(self.Q.predict(xTemp))
        qMax = np.max(qChoose, axis=1) # Q funktion für Qi+1
        r = self.rewards[learnSet]
        qNeu = (1-self.alpha)*qAlt + self.alpha*(r + self.gamma*qMax) # Y Werte für das NN Training
        self.Q.fit(x, qNeu, epochs=3, batch_size=5, verbose=False)

    #softmax funktion
    def _softmax(self,qA):
        return np.exp(qA/self.tau) / np.sum(np.exp(qA/self.tau))
    
    def chooseAction(self,qA):
        if(self.stopLearning):#falls nicht mehr gelernt werden soll exploriation ausstellen und argmax nehmen
            return np.argmax(qA) # einfach die beste Option auswählen
        else:
            toChoose = np.arange(0,len(qA))
            pW = self._softmax(qA)
            if np.any(np.isnan(pW)) or np.any(np.isinf(pW)):
                choosenA = np.random.randint(0,len(qA))
            else:
                choosenA = np.random.choice(toChoose, replace=False, p=pW) # p = Wahrscheinlichkeiten für jeden eintrag
            return(choosenA)


    
    def learn(self,status):
        #wird vom Game aufgerufen und liefert eine Aktion für einen Status
        self.memoryCounter +=1
        if not self.memoryCounter <= self.memoryMax-1:
            self.memoryCounter = 1
            self.overwriteMemory = True# Speicherüberlauf 
        if self.memoryCounter%self.updateFeq == 0 and not self.initPhase and not self.stopLearning:
            self._updateQ() 
            if self.memoryCounter % 200000 == 0:# speichere Netzwerk alle 200000 Schritte falls es zu unerwartetetem Fehler kommt
                self.saveNetwork("step")
                self.saveData("gameData",self.memoryCounter-1)
        if self.memoryCounter > min(500,self.memoryMax-1) and self.initPhase:
            self.initPhase = False
            self._initQ()
            self._updateQ()
        
        # Speicher aktuellen Status
        self.memoryStates[self.memoryCounter,:] = status
        
        #wahl einer zufalls aktion in der Initialisierungsphase
        if self.initPhase:
            self.initPhase = True
            w =  np.random.randint(self.actionAmount)
        else:#sonst Q Funktion über NN predicten und mit softmax aktion auswählen
            qA = np.zeros_like(self.a)
            j = self.memoryStates[self.memoryCounter,:].shape[0]
            x = np.zeros( (1, j+1) )
            x[0,0:j] = self.memoryStates[self.memoryCounter,:]
            try:
                for i in range(len(self.a)):
                    x[0,self.memoryStates[self.memoryCounter,:].shape[0]] = self.a[i]
                    qA[i] = self.Q.predict(x)[0,0]               
            except:
                self.saveNetwork("error")
                self.saveData("gameData",self.memoryCounter-1)
                print("Network Predicted Invalid Q Function while learning");
            ca = self.chooseAction(qA)
            w = self.a[ca]

        # Speicher aktuelle Aktion
        self.memoryActions[self.memoryCounter] = w
        return(w)

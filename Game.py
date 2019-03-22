#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import pygame
import Tetromino
import copy
import neuronalAgent
import time
import statistics as stats
 
# Überprüfen, ob die optionalen Text- und Sound-Module geladen werden konnten.
if not pygame.font: print('Fehler pygame.font Modul konnte nicht geladen werden!')
if not pygame.mixer: print('Fehler pygame.mixer Modul konnte nicht geladen werden!') 


class Game:
    
    #Konstanten für das Spiel
    DRAW_MODE_DELAY = 0.1
    
    FIELD_OFFSETX=30
    FIELD_OFFSETY=60
    FIELD_BLOCKSIZE=20

    BORDERTHICKNESS=4
    LINETHICKNESS=2

    COLOR_BACKGROUND = (35, 0 , 0)
    COLOR_BORDER= (255,255,255) #white
    COLOR_LINES= (188,188,188)

    COLOR_ONE = (10,10, 212)
    COLOR_TWO = (0 ,212, 0)

    FONT_MAIN = 0
    FONT_LOSE = 0


    GAME_FRAMERATE = 60 #Max Framerate = TickRate 
    GAME_DROPTICK = 15 #Tetromino bewegt sich alle 15 Ticks nach unten. Bei 30 FPS entspr. 0.5 Sekunden
    GAME_ROTATETICK = 14 # Wie oft Spieler Inputs ausgewertet werden
    GAME_MOVETICK = 9
    
    GAME_WIDTH = 6
    GAME_HEIGHT = 22
    
    TETROMINO_AMOUNT = 1

  
    def __init__(self, screenHeight, screenWidth, mode):
        
        self.agent = neuronalAgent.neuronalAgent(self.GAME_WIDTH)
        
        self.statistics = stats.statistics(self.agent)
        self.plotInterval = 500
        
        self.drawingMode = 1# mit Anzeige oder ohne. Zum Zeitsparen beim lernen
        self.mode = mode# Spiel Modus, KI Modus, etc ..
        self.spielfeld=  np.zeros((self.GAME_WIDTH, self.GAME_HEIGHT), dtype=int)
        self.reihen=0 #gelöschte Reihen
        self.rects = [] # alle veränderten Grafikelemente.Erhöht performance wenn nur diese gezeichnet werden.
        self.screenHeight = screenHeight
        self.screenWidth = screenWidth
        # Initialisieren aller Pygame-Module und    
        # Fenster erstellen (wir bekommen eine Surface, die den Bildschirm repräsentiert).
        pygame.init()
        self.screen = pygame.display.set_mode((screenHeight, screenWidth))
        self.tetrominoCount = 0
        self.gameCount =0
        #bestimmte events erlauben fuer performance
        #pygame.event.set_allowed([pygame.QUIT, pygame.K_DOWN, pygame.K_UP, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_SPACE])
        
        # Titel des Fensters setzen, Mauszeiger nicht verstecken und Tastendrücke wiederholt senden.
        pygame.font.init()
        self.FONT_MAIN = pygame.font.SysFont("monospace", 15)
        self.FONT_Lose = pygame.font.SysFont("monospace", 21)
        pygame.display.set_caption("Tetris Game")
        pygame.mouse.set_visible(1)
        # Wiederholt Taste gedrückt senden, auch wenn die Taste noch nicht losgelassen wurde
        pygame.key.set_repeat(100, 30)
        
        
        # Clock-Objekt erstellen, das wir benötigen, um die Framerate zu begrenzen.
        self.clock = pygame.time.Clock()
        
        self.fillBackground()  # screen-Surface mit COLOR_BACKGROUND füllen.    
        self.drawField() # zeichnet das Spielfeld
        
        pygame.display.flip() # display aktualisieren 
        # Die Schleife, und damit unser Spiel, läuft solange running == True.

        self.lost= False # spiel abbruch
    
        self.tetrominoKind = None#6 # es kann eine einzige Tetrominoart festgeschrieben werden
        self.tetrominoColor = None
        self.upcomingTetrominoList= np.arange(1,8) # Auswahl des zufälligen Tetrominos wie im original Spiel nach der "Random Bag" methode. Schränkt mögliche Tetromino Sequenzen ein
        self.upcomingTetrominoKind= 0
        # Erzeugt ein zufälliges Tetromino (tetrominoKind = None) mit der Farbe 1 (tetrominoColor = 1)
        self.upcomingTetromino = Tetromino.Tetromino(self.tetrominoKind,self.tetrominoColor)
        self.newTetromino()
        self.loop()
        self.quit()
        
    def loop(self):
        running = True
        self.__droptick = 0 #tick counter für fallenden Tetromino
        self.__movetick = 0#tick counter für Spieler Input
        self.__rotatetick = 0#tick counter für Spieler Input
        
        self.actionMove = 0 # 0 = noAction , 1= links, 2 = rechts, 3 = unten, 4= dropdown
        self.actionRotate =0 # 0 = noAction ,
        while running:
            # Alle aufgelaufenen Events holen und abarbeiten.          
            self.handleEvents()
            if self.mode == 0: #play mode
                self.handleGameTicks()
                
            if self.mode == 2: #KI modus           
                if self.actionMove != 0:
                    contourBefore = self.getGamepadOutline(3) # Bestimmung der Kontur  für den Q-Learning Agenten
                    spielfeldVorher = np.zeros_like(self.spielfeld);
                    spielfeldVorher[:,:] = self.spielfeld
                    #Status für den Agenten
                    status = np.append(contourBefore,self.tetromino.kind)
                    status = np.append(status,self.upcomingTetromino.kind)
                    cin = self.agent.learn(status)# learn liefert eine Aktion in abhängigkeit des Status
                    self.spielfeld = self.__applyAction(self.spielfeld, self.tetromino ,int(float(cin)))#Aktion aufs Spielfeld anwenden
                    deletedLines = self.isLineCompleted(np.array(range(self.GAME_HEIGHT))) #eventuell Reihen löschen
                    
                    self.agent.calcReward(deletedLines, spielfeldVorher , self.spielfeld)
                    
                    self.moveDown(19)#verhindert das Verlieren. Wird die Höhe 19 erreicht wird eine definierte Anzahl von Reihen gelöscht.
                    
                    if(self.drawingMode):# nur im Anzeige Modus zeichnen
                        self.fillBackground() 
                        self.fillOldPosition()
                        self.draw()
                        time.sleep(self.DRAW_MODE_DELAY)
                    
                    self.newTetromino()#neuer Tetromino und loop beginnt von vorne
                    
            if(self.lost == False):# falls nicht verloren wurd alle Ticks hochzahlen
                self.__droptick = self.__droptick +1
                self.__movetick = self.__movetick +1
                self.__rotatetick = self.__rotatetick +1
                self.clock.tick(self.GAME_FRAMERATE) # framerate begrenzen
            else:
                self.restartScreen()
                
        
    def quit(self):
        pygame.display.quit()
        pygame.quit()
    
    def handleGameTicks(self):# Spieler Inputs verarbeiten und Aktionen entsprechend ausführen
        if self.__droptick % self.GAME_DROPTICK == 0:
            self.fillOldPosition()
            if self.tetrominoDrop():            
                self.tetromino.moveDown()
            else:
                self.newTetromino()# neuer tetromino
                self.draw()
        if self.__movetick % self.GAME_MOVETICK ==0:
            if self.actionMove == 1:
                if self.canMoveLeft():
                    self.fillOldPosition()
                    self.tetromino.moveLeft() 
            if self.actionMove == 2:
                if self.canMoveRight():
                    self.fillOldPosition()
                    self.tetromino.moveRight()
            if self.actionMove == 3:
                if self.tetrominoDrop():
                    self.fillOldPosition()
                    self.tetromino.moveDown()    
                else:
                    self.newTetromino()# neuer tetromino
            if self.actionMove == 4:
                self.dropdown = 0
            self.draw()
            self.actionMove = 0 # 0 = noAction , 1= links, 2 = rechts, 3 = unten, 4= dropdown
        if self.__rotatetick % self.GAME_ROTATETICK == 0:      
            if self.actionRotate != 0:
                if self.canRotate():
                    self.fillOldPosition()
                    
                    self.rotations += 1
                    if( self.rotations > 3 ):
                        self.rotations = 0
                        self.actionPosition = 0
                    else:
                        positions = np.array(self.tetromino.getPositions());
                        positions[:][0]-=min(positions[:][0])
                        positions[:][1]-=min(positions[:][1])
                        possibilities =self.spielfeld.shape[0]-max(positions[:][0])
                        self.actionPosition += possibilities
                    self.tetromino.rotate(-1)
                    self.draw()
                    self.actionRotate =0 # 0 = noAction ,
           
                #tick counts
        
                    
    def handleEvents(self):#Alle Events verarbeiten
        for event in pygame.event.get():
                # Spiel beenden, wenn wir ein QUIT-Event finden.
                if event.type == pygame.QUIT:
                    self.running = False
                    self.quit()
                    
                # Wir interessieren uns auch für "Taste gedrückt"-Events.
                if event.type == pygame.KEYDOWN:
                    # Wenn Escape gedrückt wird, posten wir ein QUIT-Event in Pygames Event-Warteschlange.
                    if event.key == pygame.K_ESCAPE:
                        self.running = False               
                        pygame.event.post(pygame.event.Event(pygame.QUIT))
                        self.quit()
                    else:
                        if event.key == pygame.K_SPACE: #Leertaste startet den Agenten
                            self.actionMove = 4
                            self.mode = 2
                        else:
                            if event.key == pygame.K_BACKSPACE: #Backspace toggled den zeichen modus
                                self.drawingMode = not self.drawingMode                                        
                            if event.key == pygame.K_DOWN:#stein nach unten
                                self.actionMove=3
                            if event.key == pygame.K_UP:#stein drehen
                                self.actionRotate = -1
                            if event.key == pygame.K_LEFT:#stein nach links
                                self.actionMove=1
                            if event.key == pygame.K_SPACE:#neustart mit leertaste falls verloren wurde
                                if(self.lost):
                                    self.lost = False
                            elif event.key == pygame.K_RIGHT:#stein nach rechts
                                self.actionMove=2
                            elif event.key == pygame.K_s:#neuronales netz speichern
                                self.agent.saveNetwork("neuronalNetwork") #speichert im KI modus netz mit ab
                                self.agent.saveData("gameData", self.tetrominoCount-1)
                            elif event.key == pygame.K_l:#neuronales Netz laden und agenten nicht weiter lernen lassen
                                self.agent.stopLearning = True
                                self.agent.loadNetwork("neuronalNetwork")                            
                            elif event.key == pygame.K_i:#Spieldaten und NN lade und agenten weiter lernen lassen
                                self.agent.loadData("gameData")
                                self.agent.loadNetwork("neuronalNetwork")
                                
                                
                                
    ############## Funktionen zum Zeichnen #########################
                          
    def drawField(self):#Spielfeld zeichnen
        shape = np.shape(self.spielfeld)
        # drawing Blocks
        for i in range(shape[0]):
            for j in range(shape[1]):
                if self.spielfeld[i][j]!=0:
                    kind=self.spielfeld[i][j]
                    color = Tetromino.kindToColor(kind)
                    self.drawBlock( i , j , color)
         #drawing Gittermuster mit Rand     
        for i in range(1,shape[0]):
            self.rects.append(pygame.draw.lines(self.screen, self.COLOR_LINES, False, [(self.FIELD_OFFSETX+i*self.FIELD_BLOCKSIZE,self.FIELD_OFFSETY),(self.FIELD_OFFSETX+i*self.FIELD_BLOCKSIZE,self.FIELD_OFFSETY+self.FIELD_BLOCKSIZE*shape[1])], 1))
        for i in range(1, shape[1]):
            self.rects.append(pygame.draw.lines(self.screen, self.COLOR_LINES, False, [(self.FIELD_OFFSETX,self.FIELD_OFFSETY+i*self.FIELD_BLOCKSIZE),(self.FIELD_OFFSETX+self.FIELD_BLOCKSIZE*shape[0],self.FIELD_OFFSETY+i*self.FIELD_BLOCKSIZE)], 1))
        self.rects.append(pygame.draw.rect(self.screen, self.COLOR_BORDER, (self.FIELD_OFFSETX,self.FIELD_OFFSETY,self.FIELD_BLOCKSIZE*shape[0],self.FIELD_BLOCKSIZE*shape[1]), self.BORDERTHICKNESS))
        
        
    def fillBackground(self):
        self.screen.fill(self.COLOR_BACKGROUND)
    
    def drawBlock(self,posx,posy,color):
        self.rects.append(pygame.draw.rect(self.screen, color, (self.FIELD_OFFSETX+self.FIELD_BLOCKSIZE*posx,self.FIELD_OFFSETY+self.FIELD_BLOCKSIZE*posy,self.FIELD_BLOCKSIZE,self.FIELD_BLOCKSIZE),0));
        
    def drawTetromino(self, tetromino):
        positions = tetromino.getPositions()
        for i in range(4):
           self.drawBlock( positions[0][i],positions[1][i] ,  tetromino.color )
        
    def fillOldPosition(self):
        positions = self.tetromino.getPositions()
        for i in range(4):
            self.drawBlock( positions[0][i],positions[1][i] ,  self.COLOR_BACKGROUND )
            
    def draw(self):    
        
        # render text
        labelReihen = self.FONT_MAIN.render("Reihen: "+str(self.reihen), 1, (255,255,0))
        labelTetrominos = self.FONT_MAIN.render("Tetrominos: "+str(self.tetrominoCount), 1, (255,255,0))
        self.screen.blit(labelReihen, (150+20*self.GAME_WIDTH, 40))
        self.screen.blit(labelTetrominos, (150+20*self.GAME_WIDTH, 60))   
        self.drawTetromino(self.tetromino)
        self.drawTetromino(self.upcomingTetromino)
        self.drawField()
        pygame.display.update()
        # Inhalt von screen anzeigen.
            
            
            
    ########################### Funktionen zum verarbeiten von Aktionen  #########################
            
    def tetrominoDrop(self):#Tetromino ein Feld nach unten fallen lassen
        positions = self.tetromino.getPositions()
        for i in range(4):
            positions[1][i] = positions[1][i]+1 #upcoming move down
            if positions[1][i] >= self.spielfeld.shape[1]: #out of bounds. zuerst outofbounds pruefen wegen array index oob
                self.tetrominoMerge()
                return False
            if self.spielfeld[positions[0][i]][positions[1][i]] != 0: #position Blocked
                self.tetrominoMerge()
                return False
        return True
                           
        
    def tetrominoMerge(self):# Tetromino mit dem Spielfeld verschmelzen
        spielfeldVorher = np.zeros_like(self.spielfeld);
        spielfeldVorher[:,:] = self.spielfeld
            
        deletedLines =0
        positions = self.tetromino.getPositions()
        for i in range(4):
            self.spielfeld[positions[0][i]][positions[1][i]] = self.tetromino.kind 
        if(not self.mode == 2):# falls nicht im KI Modus wird dem Agenten der Spielerinput mitgeteilt
            #der Agent kann so auch mit Spielerinputs initialisiert werden
            deletedLines = self.isLineCompleted(np.unique(positions[1]))
            self.fillBackground() 
            
            contourBefore = self.getGamepadOutline(3)
                     
            status = np.append(contourBefore,self.tetromino.kind)           
            status = np.append(status,self.upcomingTetromino.kind)
            self.agent.memoryCounter +=1
            self.agent.memoryStates[self.agent.memoryCounter,:] = status
            self.agent.memoryActions[self.agent.memoryCounter] = self.actionPosition + self.tetromino.getPosX()
            self.agent.calcReward(deletedLines, spielfeldVorher , self.spielfeld)
            self.moveDown(15)
                           
    def isLineCompleted(self,newLineElements):# prüfen ob eine Reihe vollständig ist
        #nur reihen mit neuen bloecken ueberpruefen
        deleted = 0
        for posy in newLineElements:
            if np.all(self.spielfeld[:,posy] != 0): # reihe vollständig
                self.spielfeld = np.delete(self.spielfeld, posy, axis = 1) # reihe loeschen
                deleted = deleted + 1
                emptyRow=np.zeros((self.GAME_WIDTH,1), dtype=int)
                self.spielfeld = np.hstack((emptyRow,self.spielfeld)) #oben neue leere Reihe
                newLineElements[newLineElements<posy]=newLineElements[newLineElements<posy]-1
                self.reihen=self.reihen +1            
        return deleted
    
    def moveDown(self,top):   # verhindert das verlieren     
        y = self.spielfeld!=0
        contour = np.zeros((y.shape[0],1), dtype=int) 
        for col in range(y.shape[0]): 
            #check if row is empty
            if np.where(y[:][col])[:][0].size == 0:
                contour[col][0] = 0
            else:
                contour[col][0] = self.GAME_HEIGHT - min(np.where(y[:][col])[:][0])
                
        if(max(contour)[0]>top):
            
            self.gameCount+= 1 # Anzahl der durch diese Methode verhinderten Verluste
            
            #Auskommentieren falls nicht das gesamte Spielfeld gelöscht werden soll
            self.spielfeld=  np.zeros((self.GAME_WIDTH, self.GAME_HEIGHT), dtype=int)
            
            #Einkommentiere falls nicht das gesamte Spielfeld gelöscht werden soll
            
            #self.spielfeld = np.delete(self.spielfeld, range(self.GAME_HEIGHT-4,self.GAME_HEIGHT), axis = 1) # reihe loeschen
            #emptyRow=np.zeros((self.GAME_WIDTH,4), dtype=int)
            #self.spielfeld = np.hstack((emptyRow,self.spielfeld)) #oben neue leere Reihe
    

        
    def canRotate(self): #überprüfen ob der Tetromino rotieren kann 
        ghostTetromino = copy.copy(self.tetromino)
        ghostTetromino.rotate(-1)
        ghostPositions = ghostTetromino.getPositions()
        for i in range(4):
            positions = ghostPositions #upcoming rotate
            if positions[1][i] >= self.spielfeld.shape[1] or positions[0][i] < 0 or positions[0][i] >= self.spielfeld.shape[0]:  #out of bounds. zuerst outofbounds pruefen wegen array index oob
                return False
            if self.spielfeld[positions[0][i]][positions[1][i]] != 0: #position Blocked
                return False
        return True
        
    def canMoveLeft(self): # überprüfen ob der Tetromino nach links kann
        positions = self.tetromino.getPositions()
        for i in range(4):
            positions[0][i] = positions[0][i]-1 #upcoming move Left
            if positions[0][i] < 0: #out of bounds. zuerst outofbounds pruefen wegen array index oob
                return False
            if self.spielfeld[positions[0][i]][positions[1][i]] != 0: #position Blocked
                return False
        return True
    
    def canMoveRight(self):# überprüfen ob der Tetromino nach rechts kann
        positions = self.tetromino.getPositions()
        for i in range(4):
            positions[0][i] = positions[0][i]+1 #upcoming move Right
            if positions[0][i] >= self.spielfeld.shape[0]: #out of bounds. zuerst outofbounds pruefen wegen array index oob
                return False
            if self.spielfeld[positions[0][i]][positions[1][i]] != 0: #position Blocked
                return False
        return True
    
    
    def newTetromino(self):#neuen nächsten und übernächsten Tetromino erzeugen
        self.tetromino= self.upcomingTetromino
        startXpos = 2
        self.tetromino.start(startXpos, 0)
        self.actionPosition = 0 # starting x Position
        self.rotations = 0
        self.checkLose()# auf Verlust prüfen
        self.upcomingTetromino= Tetromino.Tetromino(self.upcomingTetrominoList[self.upcomingTetrominoKind],self.tetrominoColor)
        self.tetrominoCount+=1
        self.upcomingTetrominoKind+=1
        if(self.upcomingTetrominoKind > 6 ):# Auswahl des Tetrominos nach "Random Bag" methode
            self.upcomingTetrominoKind = 0
            np.random.shuffle(self.upcomingTetrominoList)# Shufflen der Liste welche alle 7 arten einmal enthält
        if(self.tetrominoCount % self.plotInterval == 0):
            self.statistics.plotStatistics(self.reihen,self.tetrominoCount,self.gameCount);#statistik live plotten
    
        
        
    def checkLose(self):# ist das Spiel Verloren?
        positions=self.tetromino.getPositions()
        for i in range(4):
            if self.spielfeld[positions[0][i]][positions[1][i]] != 0: #position Blocked
                self.lost = True
       
            
    # Die Funktion liefert die Kontur des Spielfeldes als Array zurück
    # ArrayIndex ist von links nach rechts im Spielfeld aufsteigend
    def getGamepadOutline(self,maxDiff):
            
        outline = np.zeros(self.GAME_WIDTH-1, dtype=int)
        sizeBefore = 0
        for y in range(self.GAME_HEIGHT):
            if self.spielfeld[0][self.GAME_HEIGHT-1-y] > 0:
                sizeBefore = y+1

        for x in range(1,self.GAME_WIDTH):
            sizeCurr = 0
            for y in range(self.GAME_HEIGHT):
                if self.spielfeld[x][self.GAME_HEIGHT-1-y] > 0:
                    sizeCurr = y+1
            diff = sizeCurr - sizeBefore
            if abs(diff) > maxDiff:
                if diff < 0:
                    diff = -maxDiff
                else:
                    diff = maxDiff
            outline[x-1] = diff
            sizeBefore = sizeCurr
        return outline
                
    #neustart Screen nach verlorenem Spiel
    def restartScreen(self):
        print("space to restart")
        labelLose = self.FONT_MAIN.render("Game Over", 1, (255,255,0))
        self.screen.blit(labelLose, ((self.screenHeight/2)-20, (self.screenWidth/2)-20))
        pygame.display.update()
        while self.lost:
            # Alle aufgelaufenen Events holen und abarbeiten.
            for event in pygame.event.get():
                # Spiel beenden, wenn wir ein QUIT-Event finden.
                if event.type == pygame.QUIT:
                    self.quit()                   
                # Wir interessieren uns auch für "Taste gedrückt"-Events.
                if event.type == pygame.KEYDOWN:
                    # Wenn Escape gedrückt wird, posten wir ein QUIT-Event in Pygames Event-Warteschlange.
                    if event.key == pygame.K_ESCAPE:            
                        pygame.event.post(pygame.event.Event(pygame.QUIT))
                        self.quit()
                    else:
                        if event.key == pygame.K_SPACE:
                            self.lost = False
        self.__init__(self.screenHeight,self.screenWidth,self.mode)   


    #Anwenden und animieren der vom Agenten ausgewählten Aktion
    def __applyAction(self, spielfeld, tetromino , actionIndex):
        rotation=0
        positions = np.array(tetromino.getPositions());
        #nur relative positionen
        positions[:][0]-=min(positions[:][0])
        positions[:][1]-=min(positions[:][1])
        #maximale verschiebungen bei aktueller rotation
        possibilities = spielfeld.shape[0]-max(positions[:][0])
        while actionIndex>possibilities-1: # maximal 3 durchläufe
            actionIndex= actionIndex - possibilities           
            rotation = rotation + 1
            if rotation>3:
                return -1 # falls actionIndex zu groß zu weit gedreht
                print("ActionIndex zu groß. Alles Falsch")
            tetromino.rotate(-1)
            if(self.drawingMode):# zeichnen falls im zeichnen modus
                self.fillBackground() 
                self.fillOldPosition()
                self.draw()
                time.sleep(self.DRAW_MODE_DELAY)#sleep damit es erkennbar ist
                self.handleEvents()
            positions = np.array(tetromino.getPositions());
            positions[:][0] = positions[:][0] - min(positions[:][0])
            positions[:][1] = positions[:][1] - min(positions[:][1])
            #maximale verschiebungen bei aktueller rotation
            possibilities = spielfeld.shape[0]-max(positions[:][0])
            
        #alle Rotationen zuEnde jetzt ist actionindex die x verschiebung
        
        if(self.drawingMode):# falls gezeichnet werden soll einfach Spielerinputs nachahmen
            while(actionIndex != tetromino.getPosX()):               
                if(actionIndex<tetromino.getPosX()):
                    tetromino.moveLeft()                   
                else:
                    tetromino.moveRight()
                self.fillBackground() 
                self.fillOldPosition()
                self.draw()
                time.sleep(self.DRAW_MODE_DELAY)
                self.handleEvents()
            while(self.tetrominoDrop()):
                self.tetromino.moveDown()
                self.fillBackground() 
                self.fillOldPosition()
                self.draw()
                time.sleep(self.DRAW_MODE_DELAY)
                self.handleEvents()
        else:#falls nicht gezeichnet werden soll das gleiche in schnell machen
            y= spielfeld[np.unique(positions[:][0] + actionIndex )][:]!=0 # y Koordinaten != 0
            contour = np.zeros((y.shape[0],1), dtype=int) 
            for col in range(y.shape[0]): # maximal 4 loops
                #check if row is empty
                if np.where(y[:][col])[:][0].size == 0: # 
                    contour[col][0] = 0
                else:
                    contour[col][0] = self.GAME_HEIGHT - min(np.where(y[:][col])[:][0])
                contour[col][0] += max(positions[1][np.where( positions[:][0] == col)[:][0]]) #- min(positions[1][np.where( positions[:][0] == col)[:][0]]) # unterste steine welche aufliegen werden
            positions[:][0] = positions[:][0] + actionIndex     #  abschließende x Koordinaten
            positions[:][1] = positions[:][1] + self.GAME_HEIGHT - max(contour) - 1 # abschließende auflage höhe.
            for i in range(4):
                self.spielfeld[positions[0][i]][positions[1][i]] = self.tetromino.kind         
        return spielfeld #Spielfeld mit gemergtem Tetromino zurückgeben.

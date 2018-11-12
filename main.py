# -*- coding: utf-8 -*-
"""
Created on Mon Nov  5 13:46:05 2018

@author: linux
"""
import numpy as np
import pygame
import Tetromino
import copy
#import Spielfeld
 
# Überprüfen, ob die optionalen Text- und Sound-Module geladen werden konnten.
if not pygame.font: print('Fehler pygame.font Modul konnte nicht geladen werden!')
if not pygame.mixer: print('Fehler pygame.mixer Modul konnte nicht geladen werden!') 

SCREEN_HEIGHT=800
SCREEN_WIDTH=600
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


GAME_FRAMERATE = 60 #Max Framerate = TickRate 
GAME_DROPTICK = 15 #Tetromino bewegt sich alle 15 Ticks nach unten. Bei 30 FPS entspr. 0.5 Sekunden
GAME_ROTATETICK = 14 # Wie oft Spieler Inputs ausgewertet werden
GAME_MOVETICK = 9

spielfeld=  np.zeros((10,18), dtype=int)
reihen=0

def quit():
    pygame.display.quit()
    pygame.quit()
    sys.exit()

def drawField(screen,spielfeld):
    rects = [] #performance
    shape = np.shape(spielfeld)
    # drawing Blocks
    for i in range(shape[0]):
        for j in range(shape[1]):
            if spielfeld[i][j]!=0:
                kind=spielfeld[i][j]
                color = Tetromino.kindToColor(kind)
                rects.append(drawBlock(screen, i , j , color))
     #drawing Gittermuster mit Rand     
    for i in range(1,shape[0]):
        rects.append(pygame.draw.lines(screen, COLOR_LINES, False, [(FIELD_OFFSETX+i*FIELD_BLOCKSIZE,FIELD_OFFSETY),(FIELD_OFFSETX+i*FIELD_BLOCKSIZE,FIELD_OFFSETY+FIELD_BLOCKSIZE*shape[1])], 1))
    for i in range(1, shape[1]):
        rects.append(pygame.draw.lines(screen, COLOR_LINES, False, [(FIELD_OFFSETX,FIELD_OFFSETY+i*FIELD_BLOCKSIZE),(FIELD_OFFSETX+FIELD_BLOCKSIZE*shape[0],FIELD_OFFSETY+i*FIELD_BLOCKSIZE)], 1))
    rects.append(pygame.draw.rect(screen, COLOR_BORDER, (FIELD_OFFSETX,FIELD_OFFSETY,FIELD_BLOCKSIZE*shape[0],FIELD_BLOCKSIZE*shape[1]), BORDERTHICKNESS))
    return rects
    
def fillBackground(screen):
    screen.fill(COLOR_BACKGROUND)

def drawBlock(screen,posx,posy,color):
    return pygame.draw.rect(screen, color, (FIELD_OFFSETX+FIELD_BLOCKSIZE*posx,FIELD_OFFSETY+FIELD_BLOCKSIZE*posy,FIELD_BLOCKSIZE,FIELD_BLOCKSIZE),0);
    
def drawTetromino(screen, tetromino):
    rects = [] #performance
    positions = tetromino.getPositions()
    for i in range(4):
        rects.append(drawBlock(screen, positions[0][i],positions[1][i] ,  tetromino.color ))
    
def fillOldPosition(screen, tetromino):
    rects = [] #performance
    positions = tetromino.getPositions()
    for i in range(4):
        rects.append(drawBlock(screen, positions[0][i],positions[1][i] ,  COLOR_BACKGROUND ))
    return rects
        
def tetrominoDrop(tetromino, spielfeld, screen):
    positions = tetromino.getPositions()
    for i in range(4):
        positions[1][i] = positions[1][i]+1 #upcoming move down
        if positions[1][i] >= spielfeld.shape[1]: #out of bounds. zuerst outofbounds pruefen wegen array index oob
            tetrominoMerge(tetromino,screen)
            return False
        if spielfeld[positions[0][i]][positions[1][i]] != 0: #position Blocked
            tetrominoMerge(tetromino,screen)
            return False
    return True
                
def tetrominoMerge(tetromino,screen):
    global spielfeld
    positions = tetromino.getPositions()
    for i in range(4):
        spielfeld[positions[0][i]][positions[1][i]] = tetromino.kind 
    isLineCompleted(np.unique(positions[1]))
    fillBackground(screen) 
        

    
def isLineCompleted(newLineElements):
    global spielfeld
    global reihen
    #nur reihen mit neuen bloecken ueberpruefen
    for posy in newLineElements:
        if np.all(spielfeld[:,posy] != 0): # reihe vollständig
            spielfeld = np.delete(spielfeld, posy, axis = 1) # reihe loeschen
            emptyRow=np.zeros((10,1), dtype=int)
            spielfeld = np.hstack((emptyRow,spielfeld)) #oben neue leere Reihe
            newLineElements[newLineElements<posy]=newLineElements[newLineElements<posy]-1
            reihen=reihen +1            
    

    
def draw(screen, tetromino, spielfeld, rects):
    #only Draw Changed
    #rects.append(fillBackground(screen))
    rects.append(drawTetromino(screen, tetromino))
    rects.append(drawField(screen , spielfeld))
    #print([rect for rect in rects if rect is not None])
    pygame.display.update()
    # Inhalt von screen anzeigen.
    
def canRotate(tetromino, spielfeld):
    ghostTetromino = copy.copy(tetromino)
    ghostTetromino.rotate(-1)
    ghostPositions = ghostTetromino.getPositions()
    for i in range(4):
        positions = ghostPositions #upcoming rotate
        if positions[1][i] >= spielfeld.shape[1] or positions[0][i] < 0 or positions[0][i] >= spielfeld.shape[0]:  #out of bounds. zuerst outofbounds pruefen wegen array index oob
            return False
        if spielfeld[positions[0][i]][positions[1][i]] != 0: #position Blocked
            return False
    return True
    
def canMoveLeft(tetromino, spielfeld):
    positions = tetromino.getPositions()
    for i in range(4):
        positions[0][i] = positions[0][i]-1 #upcoming move Left
        if positions[0][i] < 0: #out of bounds. zuerst outofbounds pruefen wegen array index oob
            return False
        if spielfeld[positions[0][i]][positions[1][i]] != 0: #position Blocked
            return False
    return True

def canMoveRight(tetromino, spielfeld):
    positions = tetromino.getPositions()
    for i in range(4):
        positions[0][i] = positions[0][i]+1 #upcoming move Right
        if positions[0][i] >= spielfeld.shape[0]: #out of bounds. zuerst outofbounds pruefen wegen array index oob
            return False
        if spielfeld[positions[0][i]][positions[1][i]] != 0: #position Blocked
            return False
    return True
    

def main():
    # Initialisieren aller Pygame-Module und    
    # Fenster erstellen (wir bekommen eine Surface, die den Bildschirm repräsentiert).
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_HEIGHT, SCREEN_WIDTH)) 
    
    #bestimmte events erlauben fuer performance
    #pygame.event.set_allowed([pygame.QUIT, pygame.K_DOWN, pygame.K_UP, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_SPACE])
    
    # Titel des Fensters setzen, Mauszeiger nicht verstecken und Tastendrücke wiederholt senden.
    pygame.font.init()
    FONT_MAIN = pygame.font.SysFont("monospace", 15)
    pygame.display.set_caption("Tetris Game")
    pygame.mouse.set_visible(1)
    # Wiederholt Taste gedrückt senden, auch wenn die Taste noch nicht losgelassen wurde
    pygame.key.set_repeat(100, 30)

    # Clock-Objekt erstellen, das wir benötigen, um die Framerate zu begrenzen.
    clock = pygame.time.Clock()
    
    
    
    
    
    
    fillBackground(screen)  # screen-Surface mit COLOR_BACKGROUND füllen.    
    drawField(screen, spielfeld)
    
    

  

    
    pygame.display.flip() 
    
    # Die Schleife, und damit unser Spiel, läuft solange running == True.
    running = True


    tetrominoKind = None
    tetrominoColor = None
    # Erzeugt ein zufälliges Tetromino (tetrominoKind = None) mit der Farbe 1 (tetrominoColor = 1)
    t = Tetromino.Tetromino(tetrominoKind,tetrominoColor)
    
    __droptick = 0 #tick counter für fallenden Tetromino
    __movetick = 0#tick counter für Spieler Input
    __rotatetick = 0#tick counter für Spieler Input
    
    actionMove = 0 # 0 = noAction , 1= links, 2 = rechts, 3 = unten, 4= dropdown
    actionRotate =0 # 0 = noAction ,
    while running:
        # Alle aufgelaufenen Events holen und abarbeiten.
        for event in pygame.event.get():
            # Spiel beenden, wenn wir ein QUIT-Event finden.
            if event.type == pygame.QUIT:
                running = False
                quit()
                
            # Wir interessieren uns auch für "Taste gedrückt"-Events.
            if event.type == pygame.KEYDOWN:
                # Wenn Escape gedrückt wird, posten wir ein QUIT-Event in Pygames Event-Warteschlange.
                if event.key == pygame.K_ESCAPE:
                    running = False               
                    pygame.event.post(pygame.event.Event(pygame.QUIT))
                    quit()
                else:
                    if event.key == pygame.K_SPACE:
                        actionMove = 4
                    else:                   
                        if event.key == pygame.K_DOWN:
                            actionMove=3
                        if event.key == pygame.K_UP:
                            actionRotate = -1
                        if event.key == pygame.K_LEFT:
                            actionMove=1
                        elif event.key == pygame.K_RIGHT:
                            actionMove=2
      
        if __droptick % GAME_DROPTICK == 0:
            rects = fillOldPosition(screen, t)
            if tetrominoDrop(t, spielfeld, screen):            
                t.moveDown()
            else:
                t = Tetromino.Tetromino(tetrominoKind,tetrominoColor)# neuer tetromino
            draw(screen, t, spielfeld,rects)
        if __movetick % GAME_MOVETICK ==0:
            if actionMove == 1:
                if canMoveLeft(t, spielfeld):
                    rects = fillOldPosition(screen, t)
                    t.moveLeft()             
            if actionMove == 2:
                if canMoveRight(t, spielfeld):
                    rects = fillOldPosition(screen, t)
                    t.moveRight()
            if actionMove == 3:
                if tetrominoDrop(t, spielfeld, screen):
                    rects = fillOldPosition(screen, t)
                    t.moveDown()    
                else:
                    t = Tetromino.Tetromino(tetrominoKind,tetrominoColor)# neuer tetromino
            if actionMove == 4:
                dropdown = 0
            draw(screen, t, spielfeld,rects)
            actionMove = 0 # 0 = noAction , 1= links, 2 = rechts, 3 = unten, 4= dropdown
        if __rotatetick % GAME_ROTATETICK == 0:      
            if actionRotate != 0:
                if canRotate(t, spielfeld):
                    rects = fillOldPosition(screen, t)
                    t.rotate(actionRotate)                
            draw(screen, t, spielfeld, rects)
            actionRotate =0 # 0 = noAction ,
            
            
            
        # render text
        labelReihen = FONT_MAIN.render("Reihen: "+str(reihen), 1, (255,255,0))
        screen.blit(labelReihen, (200, 40))
        
        
        #tick counts
        __droptick = __droptick +1
        __movetick = __movetick +1
        __rotatetick = __rotatetick +1
        clock.tick(GAME_FRAMERATE) # framerate begrenzen
        
    #wend running
    

# Überprüfen, ob dieses Modul als Programm läuft und nicht in einem anderen Modul importiert wird.
if __name__ == '__main__':
    # Unsere Main-Funktion aufrufen.
    main()
    quit()
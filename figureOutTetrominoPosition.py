#IN: Tetromino.pixels, Spielfeld
#OUT:   Positionsarray(xy) des Tetromino

import Tetromino
import numpy as np

def __checkPositionPossible(g, t):
    pos=t.getPositions()
    for i in range(pos.shape[1]):
        if pos[0][i] >= g.shape[0]:
            return False
        if pos[1][i] >= g.shape[1]:
            return False
        if g[pos[0][i]][pos[1][i]] != 0: #position Blocked
            return False
    return True


def __figureOutTerominoPosition(g, t):
    # Beginne links oben in der Spielfeldecke
    # Gehe so lange nach unten bis es nicht mehr geht
    # speicher position
    
    canRun = True

    while canRun:
        # Gehe so weit runter wie geht...
        while __checkPositionPossible(g,t):
            t.moveDown()
        print(t.getPositions())
        break
        

def figureOutTetrominoPosition(gamepad, tetromino):
    t = tetromino.copy()
    # Beschneide tetromino auf die kleinsmögliche breite und höhe
    # beschneide Null-zeilen und -Reihen
    #t = t[:,~np.all(r==0,axis=0)]
    #t = t[~np.all(r==0,axis=1)]

    t.__posX=0
    
    for x in range(gamepad.shape[0]):
        # suche für alle vier Orientierungen die Möglichkeiten heraus
        for i in range(0,4):
            # Beginne bei Positon links oben
            t.__posY=0
            
            __figureOutTerominoPosition(gamepad, t)
            t.rotate(1)
        t.moveRight()
        

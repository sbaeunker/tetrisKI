#IN: Tetromino.pixels, Spielfeld
#OUT:   Positionsarray(xy) des Tetromino

def __figureOutTerominoPosition(g, t)
    # Beginne links oben in der Spielfeldecke
    # Gehe so lange nach unten bis es nicht mehr geht
    # speicher position
    
    canRun = True

    while canRun:
        

def figureOutTetrominoPosition(gamepad, tetromino):
    t = tetromino

    # beschneide Null-zeilen und -Reihen
    t = t[:,~np.all(r==0,axis=0)]
    t = t[~np.all(r==0,axis=1)]

    # Beschneide tetromino auf die kleinsmögliche breite und höhe
    for i in range(0,4):
        __figureOutTerominoPosition(gamepad, tetromino)
        tetromino.rotate(1)
# -*- coding: utf-8 -*-
"""
Created on Mon Nov  5 13:46:05 2018

@author: linux
"""
import numpy as np
import pygame
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
COLOR_BORDER= (255,255,255) #white
COLOR_LINES= (188,188,188)


def main():
    # Initialisieren aller Pygame-Module und    
    # Fenster erstellen (wir bekommen eine Surface, die den Bildschirm repräsentiert).
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_HEIGHT, SCREEN_WIDTH)) 

    # Titel des Fensters setzen, Mauszeiger nicht verstecken und Tastendrücke wiederholt senden.

    pygame.display.set_caption("Tetris Game")
    pygame.mouse.set_visible(1)
    # Wiederholt Taste gedrückt senden, auch wenn die Taste noch nicht losgelassen wurde
    pygame.key.set_repeat(1, 30)

    # Clock-Objekt erstellen, das wir benötigen, um die Framerate zu begrenzen.
    clock = pygame.time.Clock()
    spielfeld= [[0]*18]*10
    
    #drawing:
    screen.fill((0, 0, 0))
    
    for i in range(1,len(spielfeld)):
        pygame.draw.lines(screen, COLOR_LINES, False, [(FIELD_OFFSETX+i*FIELD_BLOCKSIZE,FIELD_OFFSETY),(FIELD_OFFSETX+i*FIELD_BLOCKSIZE,FIELD_OFFSETY+FIELD_BLOCKSIZE*len(spielfeld[0]))], 1);
    for i in range(1, len(spielfeld[0])):
        pygame.draw.lines(screen, COLOR_LINES, False, [(FIELD_OFFSETX,FIELD_OFFSETY+i*FIELD_BLOCKSIZE),(FIELD_OFFSETX+FIELD_BLOCKSIZE*len(spielfeld),FIELD_OFFSETY+i*FIELD_BLOCKSIZE)], 1);
    pygame.draw.rect(screen, COLOR_BORDER, (FIELD_OFFSETX,FIELD_OFFSETY,FIELD_BLOCKSIZE*len(spielfeld),FIELD_BLOCKSIZE*len(spielfeld[0])), BORDERTHICKNESS);
    pygame.display.update()
    # Die Schleife, und damit unser Spiel, läuft solange running == True.
    running = True

    while running:
        # Framerate auf 30 Frames pro Sekunde beschränken.
        # Pygame wartet, falls das Programm schneller läuft.
        clock.tick(30)
        # screen-Surface mit Schwarz (RGB = 0, 0, 0) füllen.
        

        # Alle aufgelaufenen Events holen und abarbeiten.
        for event in pygame.event.get():
            # Spiel beenden, wenn wir ein QUIT-Event finden.
            if event.type == pygame.QUIT:
                running = False
                
            # Wir interessieren uns auch für "Taste gedrückt"-Events.
            if event.type == pygame.KEYDOWN:
                # Wenn Escape gedrückt wird, posten wir ein QUIT-Event in Pygames Event-Warteschlange.
                if event.key == pygame.K_ESCAPE:
                    running = False
                    pygame.display.quit()
                    pygame.quit()
                    pygame.event.post(pygame.event.Event(pygame.QUIT))

        # Inhalt von screen anzeigen.
        pygame.display.flip()

# Überprüfen, ob dieses Modul als Programm läuft und nicht in einem anderen Modul importiert wird.
if __name__ == '__main__':
    # Unsere Main-Funktion aufrufen.
    main()
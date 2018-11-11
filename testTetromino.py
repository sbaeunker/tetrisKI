# -*- coding: utf-8 -*-
"""
Created on Mon Nov  5 14:36:51 2018

@author: linux
"""

import Tetromino

tetrominoColor = 1
tetrominoKind = None
# Erzeugt ein zufälliges Tetromino (tetrominoKind = None) mit der Farbe 1 (tetrominoColor = 1)
t = Tetromino.Tetromino(tetrominoKind,tetrominoColor)

# in pixels steht ein 3x3 Pixelbild des Tetromino, dass an allen belegten Pixeln die Farbe und an allen anderen Stelle 0 enthält
print("Tetromino Anordnung:")
print(t.pixels)
print()

# rotiere das Tetromino um 90° im Uhrzeigersinn
t.rotate(1)
print("Tetromino um 90Grad im Uhrzeigersinn gedreht:")
print(t.pixels)
print()

# rotiere das Tetromino um 90° gegen den Uhrzeigersinn
t.rotate(-1)
print("Tetromino um 90Grad gegen den Uhrzeigersinn gedreht")
print(t.pixels)
print()

print(t.getPositions())
t.moveDown()
t.moveDown()
t.moveDown()
t.moveLeft()
print(t.getPositions())
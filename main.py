#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 22 11:20:10 2018

@author: stefan
"""
import Game

def main():
    game = Game.Game(800,600,0)
    #mode 0 = playMode
    #mode 1 = agentLearning ohne Grafik
    #mode 2 = agentLearning mit Grafik
    #mode 3 = debug
    
    # Überprüfen, ob dieses Modul als Programm läuft und nicht in einem anderen Modul importiert wird.
if __name__ == '__main__':
    main()
 
# tetrisKI
Angewandte KI, HS Bochum, tetrisKI

Im Rahmen dieses Projektes soll das Tetris-Spiel nachprogrammiert werden und von einer KI gelernt werden.

## Was ist Q-Learning

## Unser Ansatz
- Für jeden Tetromino wird ein Agent geschrieben
- Die Agenten unterscheiden sich hauptsächlich durch ihre Aktionen
- Als Zustand wird die Kontur des Spielfeldes und der aktuelle, sowie der nächste Tetromino übergeben
- Als Aktion wird eine tetromino-spezifische Nummer zurückgegeben, die angibt in welcher Spalte der Tetromino abgelegt werden  soll und wie oft dieser gedreht werden soll

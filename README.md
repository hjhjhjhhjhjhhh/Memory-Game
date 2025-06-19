# Memory-Game

## Introduction 
This is a game made for 新竹台大老年醫院

## Packages 
- pygame 
- pyinstaller 


## How to Run 
```
python main.py 
```

## Compile to exe file
```
pyinstaller --onefile --noconsole --add-data "images;images" --add-data "bgm.mp3;." --add-data "MSJHBD.TTC;." main.py
```
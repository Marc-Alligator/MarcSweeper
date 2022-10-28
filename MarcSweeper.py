import sys, math, time, pygame, random
pygame.init()
pygame.font.init()


initialCellFillColor = pygame.Color(223,223,223)
initialCellBrighterColor = pygame.Color(255,255,255)
initialCellDarkerColor = pygame.Color(63,63,63)
steppedOnCellFillColor = pygame.Color(191,191,191)
steppedOnCellBorderColor = pygame.Color(127,127,127)
steppedOnMineCellFillColor = pygame.Color(191,0,0)
flagTopColor = pygame.Color(255,63,63)
flagPostColor = pygame.Color("black")
flagBaseColor = pygame.Color("black")
mineColor = pygame.Color("black")
maxWindowWidth = 1920
maxWindowHeight = 1000
cellSize = 40
colorDict = {"?":pygame.Color("black"),
             1:pygame.Color("blue"),
             2:pygame.Color("darkgreen"),
             3:pygame.Color("red"),
             4:pygame.Color("darkblue"),
             5:pygame.Color("darkred"),
             6:pygame.Color("darkcyan"),
             "counters":pygame.Color("red"),
             "topBarBG":pygame.Color("black"),
             "X":pygame.Color("red")}
difficultyDict = {'beginner':[12,12,5/32], 'intermediate':[23,23,5/32], 'expert':[40,21,0.23]} #lists have cellsInX, cellsInY, and mineFrequency (out of one)

CLOCKEVENT = pygame.event.custom_type()

def colorOf(inputVal):
    global colorDict
    if inputVal in colorDict:
        return colorDict[inputVal]
    else:
        return pygame.Color("black")

def screenX(x):
    global cellSize
    return round(cellSize*x)
def screenY(y):
    global cellSize
    return round(cellSize*(y+1))
def cellX(x): #is redundant information, inverse of screenX and screenY
    global cellSize
    return math.floor(x/cellSize)
def cellY(y):
    global cellSize
    return math.floor(y/cellSize-1)

def drawBlankCell(x,y):
    pygame.draw.rect(window,initialCellFillColor,((screenX(x),screenY(y)),(cellSize,cellSize)),0)
    pygame.draw.lines(window,initialCellBrighterColor,False,((screenX(x)+1,screenY(y+1)),  (screenX(x)+1,  screenY(y)+1),  (screenX(x+1),  screenY(y)+1)),2)
    pygame.draw.lines(window,initialCellDarkerColor,  False,((screenX(x)+1,screenY(y+1)-1),(screenX(x+1)-1,screenY(y+1)-1),(screenX(x+1)-1,screenY(y)+1)),2)

referencePointDict = {"left":0,"center":0.5,"right":1}
def textAtScreenCoords(screenX,screenY,referencePoint,inputStr,textColor,fillColor):
    tempTextSurface=fontUsed.render(inputStr,True,textColor,fillColor)
    screenX-=referencePointDict[referencePoint]*tempTextSurface.get_width()
    window.blit(tempTextSurface,(round(screenX),round(screenY)))
    
def charAtCell(cellX,cellY,inputVal,fillColor):
    textAtScreenCoords(screenX(cellX+0.5),screenY(cellY+0.1),"center",str(inputVal),colorOf(inputVal),fillColor)
class Cell:
    def __init__(self,x,y):
        global initalCellColor
        self.x=x
        self.y=y
        self.hasMine=False
        self.hasBeenSteppedOn=False
        self.isFlagged=False # 1 is flagged; 2 is '?'
        self.flagStatus = '0'
        drawBlankCell(self.x,self.y)
    def tryToGiveMine(self):
        if not self.hasMine:
            self.hasMine=1
            global cellsWithMines
            cellsWithMines.append(self)
            return True
        else:
            return False
    def leftClick(self):
        if self.flagStatus != 'F' and not self.hasBeenSteppedOn:
        #if self.hasBeenSteppedOn==0 and self.isFlagged!=1:
                self.stepOn()
                
        elif self.countMinesAround()==self.countFlagsAround():
            self.stepAround()
        pygame.display.flip()
    def cellFill (self,fillColor):
        pygame.draw.rect(window,fillColor,((screenX(self.x),screenY(self.y)),(cellSize,cellSize)),0)
    def cellBorder (self,borderColor):
        pygame.draw.rect(window,borderColor,((screenX(self.x),screenY(self.y)),(cellSize,cellSize)),1)
    def drawSelf(self):
        
        if self.hasBeenSteppedOn:
            self.cellFill(steppedOnCellFillColor)
            minesAround = self.countMinesAround()
            if minesAround:
                charAtCell(self.x,self.y,minesAround,steppedOnCellFillColor)
            self.cellBorder(steppedOnCellBorderColor)
        else:
            drawBlankCell(self.x,self.y)
            if self.flagStatus == 'F':
                charAtCell(self.x,self.y,'F',initialCellBrighterColor)
            elif self.flagStatus == '?':
                charAtCell(self.x,self.y,'?',initialCellBrighterColor)
            #... fixme


        
    def stepOn(self):
        self.hasBeenSteppedOn=1
        global cellsSteppedOn
        cellsSteppedOn+=1
        if self.hasMine:
            for cellWithMine in cellsWithMines:
                cellWithMine.cellFill(steppedOnMineCellFillColor)
                pygame.draw.circle(window,mineColor,(screenX(cellWithMine.x+1/2),screenY(cellWithMine.y+1/2)),(cellSize//2-2),0)
                cellWithMine.cellBorder(steppedOnCellBorderColor)
            pygame.display.flip()
            print("you died! :( click to exit")
            while pygame.mouse.get_pressed()!=(0,0,0):
                pygame.event.wait()
            while pygame.mouse.get_pressed()!=(1,0,0):
                pygame.event.wait()
            exit()
        else:
            self.cellFill (steppedOnCellFillColor)
            minesAround = self.countMinesAround()
            if minesAround:
                charAtCell(self.x,self.y,minesAround,steppedOnCellFillColor)
            else:
                self.stepAround()          
            
        self.cellBorder(steppedOnCellBorderColor)
        #pygame.draw.rect(window,steppedOnCellBorderColor,((screenX(self.x),screenY(self.y)),(cellSize,cellSize)),1)
    def around(self):
        cellsAround=[]
        for x in range(self.x-1,self.x+2):
            for y in range(self.y-1,self.y+2):
                if x>=0 and y>=0 and x<cellsInX and y<cellsInY and not (x==self.x and y==self.y):
                    cellsAround.append(allCells[x][y])
        return cellsAround
    def stepAround(self):
        for cellAround in self.around():
            if cellAround.hasBeenSteppedOn==0 and cellAround.isFlagged==0:
                cellAround.stepOn()
    def countMinesAround(self):
        countOfMines=0
        for cellAround in self.around():
            countOfMines+=cellAround.hasMine
        return countOfMines
    def countFlagsAround(self):
        countOfFlags=0
        for cellAround in self.around():
            if cellAround.isFlagged == 1:
                countOfFlags+=1
        return countOfFlags
    def tryToFlag(self):
        if self.hasBeenSteppedOn==0:
            drawBlankCell(self.x,self.y)
            global minesToFlag
            self.isFlagged+=1
            if self.isFlagged==1:
                self.flagSTatus = 'F'
                pygame.draw.rect(window,flagBaseColor,((screenX(self.x+0.23 ),screenY(self.y+0.7)),(round(cellSize*0.54),round(cellSize*0.15))),0)
                pygame.draw.rect(window,flagPostColor,((screenX(self.x+0.45),screenY(self.y+0.2)),(round(cellSize*0.1),round(cellSize*0.6))),0)
                pygame.draw.polygon(window,flagTopColor,((screenX(self.x+0.55),screenY(self.y+0.1)),(screenX(self.x+0.55),screenY(self.y+0.5)),(screenX(self.x+0.2),screenY(self.y+0.3))))
                minesToFlag-=1
            elif self.isFlagged==2:
                self.flagStatus = '?'
                charAtCell(self.x,self.y,"?",initialCellFillColor)
                minesToFlag+=1
            elif self.isFlagged==3:
                self.flagStatus = '0'
                self.isFlagged=0
            pygame.display.flip()

#choose difficulty
noDifficultySelected=True
while noDifficultySelected:
    #difficulty=input("Would you like a beginner, intermediate, or expert difficulty? ")
    difficulty = "intermediate"
    noDifficultySelected=False
    if difficulty in difficultyDict:
        cellsInX = difficultyDict[difficulty][0]
        cellsInY = difficultyDict[difficulty][1]
        mineFrequency = difficultyDict[difficulty][2]
    elif difficulty == "custom":
        cellsInX = int(input("How many cells wide?"))
        cellsInY = int(input("How many cells tall?"))
        mineFrequency = float(input("what proportion of cells do you want to have mines?"))
    else:
        print("That is not an option I know.")
        noDifficultySelected=True
totalMines = round(cellsInX*cellsInY*mineFrequency)
minesToFlag = totalMines#to start off
#determines optimal cell size if they need to be shrunk to fit on the screen
while screenX(cellsInX) > maxWindowWidth:
    cellSize -=1
while screenY(cellsInY) > maxWindowHeight:
    cellSize -=1
fontUsed = pygame.font.Font(None,round(cellSize*1.23))
window=pygame.display.set_mode((screenX(cellsInX),screenY(cellsInY)),pygame.RESIZABLE)
pygame.display.set_caption("MarcSweeper")

quitProgram = False
while not quitProgram:
    allCells=[]
    cellsWithMines=[]
    for x in range(0,cellsInX):
        newColumn=[]
        for y in range(0,cellsInY):
            newCell=Cell(x,y) #creates every cell
            newColumn.append(newCell)
        allCells.append(newColumn)
    pygame.display.flip()
    minesLaid=0
    cellsSteppedOn=0
    
    # until game is over
    cellsLeftToStepOn = cellsSteppedOn<cellsInX*cellsInY-totalMines
    while cellsLeftToStepOn and not quitProgram:
        #handle events
        newEvent = pygame.event.wait()#waits for input
        #click event
        if newEvent.type == pygame.MOUSEBUTTONDOWN:
            button = newEvent.dict['button']
            if button == 1:
                leftClick = True
            else:
                leftClick = False
            if button == 3:
                rightClick = True
            else:
                rightClick = False
            screenPos = newEvent.dict['pos']
            mouseCellX = cellX(screenPos[0])
            mouseCellY = cellY(screenPos[1])
            
            if mouseCellX in range(0,cellsInX) and mouseCellY in range(0,cellsInY):
                if leftClick:#if user leftclicks on a cell
                    if minesLaid==0:

# INITIALIZE
                        while minesLaid<totalMines:
                            x=math.floor(random.random()*cellsInX)
                            y=math.floor(random.random()*cellsInY)
                            if not (x==cellX(pygame.mouse.get_pos()[0]) and y==cellY(pygame.mouse.get_pos()[1])):
                                    minesLaid += allCells[x][y].tryToGiveMine()
                        startTime=time.time()
                        pygame.time.set_timer(pygame.event.Event(CLOCKEVENT),100)
                    allCells[mouseCellX][mouseCellY].leftClick()
                    pygame.display.flip()

                elif rightClick:#if user rightclicks on a cell
                    allCells[mouseCellX][mouseCellY].tryToFlag()
                    
                    
            elif leftClick and mouseCellX==cellsInX-1 and mouseCellY==-1:
                quitProgram = True
                #exit()


                    
        #clock event
        elif newEvent.type == CLOCKEVENT:
            pygame.draw.rect(window,colorDict["topBarBG"],((0,0),(screenX(cellsInX),screenY(0))),)
            textAtScreenCoords(0,                  0,"left", str(round(time.time()-startTime)),colorDict["counters"],colorDict["topBarBG"])
            textAtScreenCoords(screenX(cellsInX-1),0,"right",str(minesToFlag),                 colorDict["counters"],colorDict["topBarBG"])
            charAtCell(cellsInX-1,-1,"X",colorDict["topBarBG"])
            pygame.display.flip()
            pygame.time.set_timer(pygame.event.Event(CLOCKEVENT),100)

        #window resize event
        elif newEvent.type == pygame.VIDEORESIZE:
            (screenWidth,screenHeight) = newEvent.dict['size']
            maxCellSizeX = math.floor(screenWidth/cellsInX)
            maxCellSizeY = math.floor(screenHeight/(cellsInY+1))
            cellSize = min([maxCellSizeX,maxCellSizeY])
            fontUsed = pygame.font.Font(None,round(cellSize*1.23))

            #redraw
            for column in allCells:
                for cell in column:
                    cell.drawSelf()

        #Calculate if while-loop should run again.
        cellsLeftToStepOn = cellsSteppedOn<cellsInX*cellsInY-totalMines
        
    print("you win! click to replay")
    while pygame.mouse.get_pressed()!=(1,0,0):
        pygame.event.wait()
#exit()


from numpy.core.numeric import isclose
from AI import AI
from Action import Action

import numpy as np
from collections import OrderedDict, deque, defaultdict
import random

class Board():
	# Flag = -2 #Cover = -1 
    _Flag = -2
    _Cover = -1
    _ValidRange = range(-2,9)

    def __init__(self,rowD,colD,startx,starty,total_mines):
	    self.board = np.full((rowD,colD),self._Cover,dtype=np.int8)
	    self.totalM = total_mines
	    self.rowD = rowD
	    self.colD = colD
	
    def __getitem__(self,item):
	    return self.board[item]
	
    def __setitem__(self,item,value):
	    self.board[item] = value

	#count the number of uncover/cover/flag of the board
    def reportBoard(self):
	    #return defaultdict(int, zip(*np.unique(self.board,return_counts=True)))
        adict = defaultdict(int)
        for i in self.board:
            for j in i:
                adict[j]+=1
        return adict

    #Update the board at the position
    def update_board(self,x,y,value):
	    self.board[x,y] = value

    def flag(self,x,y):
	    self.board[x,y] = self._Flag
  
    def boundCheck(self,x,y):
	    return (0<=x<self.rowD) and (0<=y<self.colD)

	#create Window object from (0,0) to (n,n)
    def window_iter(self,fieldEdge = True):
        
        if fieldEdge == True:
            return (Window(self,x,y) for x in range(self.board.shape[0]) 
           		    for y in range(self.board.shape[1]))
        else:
            return (Window(self,x,y) for x in range(self.board.shape[0]-1) 
           			for y in range(self.board.shape[1]-1))
   
    def lambdaBoard(self,coord,func):
        return [c for c in coord if func(self.board[c])]
        
#This class split the function into 2*2 or 3*3 board to exam any open tiles
class Window():
    def __init__(self,board:Board,x,y):
	    self.board = board
	    self.window = self.board[max(0,x-1):min(x+2,self.board.rowD),max(0,y-1):min(y+2,self.board.colD)]
	    self.currentCod = (x,y)
        
        
    def centerWindow(self):
	    return tuple(min(self.currentCod[0],1),min(self.currentCod[1],1))

    def adj(self):
	    adjList = [(x+self.currentCod[0],y+self.currentCod[1]) for x in range(-1,2) for y in range(-1,2) if (x, y) != (0, 0)]
	    return [adj for adj in adjList if self.board.boundCheck(adj[0],adj[1])]

    def __getitem__(self,item):
	    return self.window[item]

    def __setitem__(self,item,value):
	    self.window[item] = value
  
    def remaining(self):
	    self.tValue = self.board[self.currentCod]

	    flagNum = self.window[self.window==Board._Flag].size
	    coverNum = self.window[self.window==Board._Cover].size

	    return self.tValue-flagNum, flagNum, coverNum
 
    def score(self):
        return self.board[self.currentCod]
    
    


class MyAI(AI):
    
    def __init__(self, rowDimension, colDimension, totalMines, startX, startY):
        # init a board with Board class
        self.board = Board(colDimension, rowDimension, startX, startY, totalMines)
        self.totalMines = totalMines
        
        self.frontier = Frontier()
        self.uncovered = set()
        self.frontier.enqueue((startX, startY))

        #Prevent visiting any visited tiles 
        self.explored = set()

        # Action queue
        self.action_queue = deque()
        self.current_action = Action(AI.Action.UNCOVER, startX, startY)
		

	#Test if the board reach the goal 	
    def goalTest(self):
        unCoverNum = self.board.reportBoard()
        
        if unCoverNum[Board._Cover] == 0:
            return True
        else:
        	return False
    #The main algorithm function, find all the open tiles until can't find, then make random move
    def aiAlgorithm(self):
        
        while True:
            if len(self.action_queue) != 0:
                return
            if self.goalTest() == True:
                self.action_queue.append(Action(AI.Action.LEAVE))
                return
                
            if len(self.action_queue) == 0:
                
                for w in self.board.window_iter():
                    if w.score() >= 0:
                        self.randomRule(w)
                
                
                if len(self.frontier) == 0 or len(self.action_queue) == 0:
                    
                    self.uncover_random()
                    return
                
            nextExplore = self.frontier.dequeue()
            w = Window(self.board,nextExplore[0],nextExplore[1])
            if w.currentCod in self.explored:
                continue
            
            self.randomRule(w)
            
    
    def getAction(self, number: int):
        
        if number != -1:
            update_info = (self.current_action.getX(),self.current_action.getY(),number)
            self.board.update_board(*update_info)
            
        
        if len(self.action_queue) == 0:
            self.aiAlgorithm()
            
            if len(self.action_queue) == 0:
                return Action(AI.Action.LEAVE)
        
        self.current_action = self.action_queue.popleft()
       
        return self.current_action
	
         
    def uncover_random(self):
        result = np.where(self.board.board==Board._Cover)
        coverList = np.dstack(np.array(list(result))).reshape((-1,2))
        
        safeList = []
        for c in coverList:
            w = Window(self.board, c[0],c[1])
            if np.all(w.window<=0):
                safeList.append(c)
        if len(safeList) == 0:
            uncovered = tuple(random.choice(coverList))
            self.action_queue.append(Action(AI.Action.UNCOVER,uncovered[0],uncovered[1]))
            self.frontier.enqueue(uncovered)
        else:
            uncovered = tuple(random.choice(safeList))
            self.action_queue.append(Action(AI.Action.UNCOVER,uncovered[0],uncovered[1]))
            self.frontier.enqueue(uncovered)
        
              
    
    def searchBasics(self):
        actions = []
        for x,y in self.frontier.copy():
            curWindow = Window(self.board,x,y)
            remaining,flagNum, coverNum = curWindow.remaining()
            uncovered = [i for i in curWindow.adj() if curWindow.board[i] == Board._Cover]
            
            if remaining == 0:
                
                for x,y in uncovered:
                    if (x,y) not in self.discover:
                        actions.append(Action(AI.Action.UNCOVER,x,y))
                        self.frontier.append((x,y))
                        self.discover.add((x,y))
                
            elif curWindow.tValue == coverNum+flagNum and self.totalMines != 0:
                for x,y in zip(uncovered[0],uncovered[1]):
                    #actions.append(Action(AI.Action.FLAG,x,y))
                    self.board.flag(x,y)
                    self.totalMines-=1
        
        return actions
             
             
    def randomRule(self,w:Window):
        
        if w.score()<0:
            return
        remainTuple = w.remaining()
        if remainTuple[0] == 0:
            uncoverList = self.board.lambdaBoard(w.adj(),lambda x: x == Board._Cover)
            for t in uncoverList:
                self.action_queue.append(Action(AI.Action.UNCOVER,t[0],t[1]))
        elif remainTuple[0] == remainTuple[2]:
            flagList = self.board.lambdaBoard(w.adj(),lambda x: x == Board._Cover)
            for t in flagList:
                self.action_queue.append(Action(AI.Action.FLAG,t[0],t[1]))
                self.board.flag(t[0],t[1])
            else:
                return
        for adj in w.adj():
            self.frontier.enqueue(adj)
        
        if remainTuple[2] == 0:
            self.explored.add(w.currentCod)
                
    
class Frontier(OrderedDict):
    def enqueue(self, key, value=None):
        self.__setitem__(key, value)

    def dequeue(self):
        return self.popitem(last=False)[0]
    
    
  

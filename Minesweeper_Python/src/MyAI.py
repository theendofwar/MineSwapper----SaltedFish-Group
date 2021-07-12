
from AI import AI
from Action import Action

import numpy as np
from collections import OrderedDict, deque, defaultdict
from traceback import print_exc
import itertools as it
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
		a = defaultdict(int)
		for i in self.board:
			for j in i:
				a[j]+=1
		return a

    #Update the board at the position
	def update_board(self,x,y,value):
		self.board[x,y] = value

	def flag(self,x,y):
		self.board[x,y] = self._Flag
  
	def boundCheck(self,x,y):
		return (0<x<self.rowD) and (0<y<self.colD)

	#create Window object from (0,0) to (n,n)
	def window_iter(self,fieldEdge = True):
     
		if fieldEdge == True:
			return (Window(x,y) for x in range(self.board.shape[0]) 
           			for y in range(self.board.shape[1]))
		else:
			return (Window(x,y) for x in range(self.board.shape[0]-1) 
           			for y in range(self.board.shape[1]-1))
        
#You can ignore this class, it split the board into 2x2 or 3x3 board for finding any specific patterns	
class Window():

	def __init__(self,board:Board,x,y):
		self.board = board
		self.window = self.board[max(0,x-1):min(x+2,self.board.rowD),max(0,y-1):min(y+2,self.board.colD)]
		self.currentCod = (x,y)
	
	def centerWindow(self):
		return (min(self.currentCod[0],1),min(self.currentCod[1],1))

	def adj(self):
		adjList = [(x+self.currentCod[0],y+self.currentCod[1]) for x in range(-1,2) for y in range(-1,2)]
		return [adj for adj in adjList if self.board.boundCheck(adj[0],adj[1])]

	def __getitem__(self,item):
		return self.window[item]

	def __setitem__(self,item,value):
		self.window[item] = value
  
	def remaining(self):
		tValue = self.board[self.currentCod]

		flagNum = self.window[self.window==Board._Flag].size
		coverNum = self.window[self.window==Board._Cover].size

		return tValue-flagNum, flagNum, coverNum


		



class MyAI(AI):
    """
    My AI class.
    """
    def __init__(self, rowDimension, colDimension, totalMines, startX, startY):
        # Minefield state
        self.mf = Board(colDimension, rowDimension, startX, startY, totalMines)
        self.totalMines = totalMines
        # Add starting point to the expansion
        # Frontier is some kind of FIFO here. We just need constant-time
        # enqueue, dequeue, and membership testing, which OrderedDict has.
        # See https://stackoverflow.com/questions/8176513/ for more info
        self.frontier = Frontier()
        self.frontier[startX] = startY

        # Fully exhausted on this run (won't come back again)
        self.explored = set()

        # Action queue
        self.action_queue = deque()
        # The agent took this action and now it is waiting for the percept.
        # This action is already taken by the game when it starts
        self.current_action = Action(AI.Action.UNCOVER, startX, startY)
		

	#Test if the board reach the goal 	
    def goalTest(self):
        unCoverNum = self.mf.reportBoard()
        print(unCoverNum)
        if unCoverNum[Board._Cover] == 0:
            return True
        else:
        	return False
    #Your algorithm should go here
    def aiAlgorithm(self):
        while True:
            if len(self.action_queue) != 0:
                return
            if self.goalTest() == True:
                self.action_queue.append(Action(AI.Action.LEAVE))
                return
            
            if self.totalMines != 1:
                print('put mine')
                minesLocation = self.searchBasics()
                if len(minesLocation)>0:
                    self.action_queue.extend(minesLocation)  
                    return
            
            if len(self.frontier) == 0 or len(self.action_queue) == 0:
                print('random move')
                self.uncover_random()
                return
            
    # You could modify this function, I think it is working
    def getAction(self, number: int):
        print("start")
        if number != -1:
            update_info = (self.current_action.getX(),self.current_action.getY(),number)
            self.mf.update_board(*update_info)
        
        if len(self.action_queue) == 0:
            self.aiAlgorithm()
            
            if len(self.action_queue) == 0:
                return Action(AI.Action.LEAVE)
        
        self.current_action = self.action_queue.popleft()
        return self.current_action
	
    #ignore this        
    def uncover_random(self):
        print('random move function')
        # Select the unflagged tiles
        where_result = np.where(self.mf.board==self.mf._Flag)
        unflagged_tiles = self.mf.board
        print(unflagged_tiles)
        print(where_result)
        # Remove tiles next to an unflagged one
        unflagged_safe = []
        for coord in unflagged_tiles:
            node = Window(self.mf, *coord)
            # Don't want tiles with uncovered tiles around them
            if np.all(node.window<=0):
                unflagged_safe.append(coord)

        # If none are left, fall back to the unfiltered list
        if len(unflagged_safe) == 0:
            unflagged_safe = unflagged_tiles

        # Pick one and live with it
        coord_to_uncover = tuple(random.choice(unflagged_safe))
        print("Coord_to_cover",coord_to_uncover)
        self.action_queue.append(
            Action(AI.Action.UNCOVER, *coord_to_uncover)
        )
        self.frontier.enqueue(coord_to_uncover)
        
        
    
        
				
					
	
				

              
    #ignore this
    def searchBasics(self):
        actions = []
        for window in self.mf.window_iter(field_edges=False):
             avaliable = window.remaining()[2]
             if avaliable == 1 and window.window[1,1] == 1:
                xyLists =[(x,y) for x in range(window.window.shape[0]) for y in range(window.window.shape[1]) if window.window[x,y] == Board._Cover]
                print(xyLists)
                actions.append(Action(AI.Action.FLAG),xyLists[0],xyLists[1])
                self.totalMines-=1
    
        return actions
             
    
class Frontier(OrderedDict):
    def enqueue(self, key, value=None):
        # Does nothing if the key is already in the queue
        self.__setitem__(key, value)

    def dequeue(self, get_value=False):
        if get_value:
            return self.popitem(last=False)
        else:
            return self.popitem(last=False)[0]
    
    
#!/usr/bin/env python3
import math
import random
import sys
import time
from fishing_game_core.game_tree import Node
from fishing_game_core.player_utils import PlayerController
from fishing_game_core.shared import ACTION_TO_STR, TYPE_TO_SCORE
def printD(*a):
    print(*a, file=sys.stderr)

class PlayerControllerHuman(PlayerController):
    def player_loop(self):
        while True:
            # send message to game that you are ready
            msg = self.receiver()
            if msg["game_over"]:
                return


class PlayerControllerMinimax(PlayerController):

    def __init__(self):
        super(PlayerControllerMinimax, self).__init__()
        self.t = None

    def player_loop(self):
        first_msg = self.receiver()

        while True:
            msg = self.receiver()
            # Create the root node of the game tree
            node = Node(message=msg, player=0)
            # Possible next moves: "stay", "left", "right", "up", "down"
            self.t = time.time()
            best_move = None
            i = 1
            timeOut = False
            val = float('-inf')
            while not timeOut:
                printVal, move, timeOut = self.search_best_next_move(currNode = node, depthLeft = i, alpha = float('-inf'), beta = float('inf'), greenBoat = True)
                if printVal > val:
                    best_move = move
                    val = printVal
                #printD("@ @ @ @ @ INNER Depth: " + str(i) + " Has the Best Move: " + move + " With Score: " + str(printVal))
                i += 1
            #printD("- - - - OUTER Depth: " + str(i) + " Has the Best Move: " + move + " With Score: " + str(printVal))
            self.sender({"action": best_move, "search_time": None})

    def euclDistance(self, fishPos, hookPos):
        dist = ((fishPos[0] - hookPos[0])**2) + ((fishPos[1] - hookPos[1])**2)
        return dist

    def evaluate(self, currNode):
        fishCaught = currNode.state.get_caught()		
        currScores = currNode.state.get_player_scores()		
        fishPos = currNode.state.get_fish_positions()		
        hookPos = currNode.state.get_hook_positions()		
        fishScores = currNode.state.get_fish_scores()

        greenScore = 0		
        redScore = 0		
        dist = 0			
        if fishCaught[0] is None:		
            for fish in fishPos:		
                if fishScores[fish] > 0:		
                    dist = self.euclDistance(fishPos[fish], hookPos[0])
                    if dist == 0:	
                        greenScoreTemp = float('inf')	
                    else:
                        greenScoreTemp = fishScores[fish]*math.exp(-dist)
                    if greenScoreTemp > greenScore:
                        greenScore = greenScoreTemp			
                                
        else:		
            greenScore = fishScores[fishCaught[0]]
        
        if fishCaught[1] is None:		
            redScore = 0
                                
        else:		
            redScore = fishScores[fishCaught[0]]

        eval = 2*currScores[0] + greenScore - currScores[1]*2 -redScore
        #printD("Current Node: " + str(ACTION_TO_STR[currNode.move]) + " has the Score: " + str(eval))		
        return eval

    def search_best_next_move(self, currNode, depthLeft, alpha, beta, greenBoat):

        if time.time() - self.t >= 0.055:
            eval = self.evaluate(currNode)
            if currNode.move is None:
                nextAct = 0
            else:
                nextAct = ACTION_TO_STR[currNode.move]
            return eval, nextAct, True

        children = currNode.compute_and_get_children()
        #children.sort(key=self.evaluate, reverse=True)
        
        if depthLeft == 0 or len(children) == 0:
            eval = self.evaluate(currNode)
            nextAct = ACTION_TO_STR[currNode.move]
            return eval, nextAct, False

        if greenBoat:
            maxEval = float('-inf')
            nextAct = "stay"
            for child in children:
                eval, myAct, timeOut = self.search_best_next_move(child, depthLeft - 1, alpha, beta, False)
                if eval > maxEval:
                    maxEval = eval
                    nextAct = myAct
                alpha = max(alpha, maxEval)
                if beta <= alpha:
                    break
            #printD("DEPTH: " + str(depthLeft) + " Green: " + str(maxEval) + " For MOVE: " + nextAct)
            return maxEval, nextAct, timeOut
        else:
            minEval = float('inf')
            nextAct = "stay"
            for child in children:
                eval, myAct, timeOut = self.search_best_next_move(child, depthLeft - 1, alpha, beta, True)

                if eval < minEval:
                    minEval = eval
                    nextAct = myAct
                beta = min(minEval, beta)
                if beta <= alpha:
                    break
            #printD("Red: " + str(minEval) + " For MOVE: " + nextAct)
            return minEval, nextAct, timeOut


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
            printVal = 0
            val = float('-inf')
            try:
                while True:
                    printVal, move= self.search_best_next_move(currNode = node, depthLeft = i, alpha = float('-inf'), beta = float('inf'), greenBoat = True)
                    #if printVal > val:
                    best_move = move
                    val = printVal
                    i += 1
                    printD("INNER Depth: " + str(i-1) + " Move: " + str(move) + " Value: " + str(printVal))
            except:
                # Execute next action
                printD("OUTER Depth: " + str(i) + " Move: " + str(best_move) + " Value: " + str(printVal))
                self.sender({"action": best_move, "search_time": None})



    def euclDistance(self, fishPos, hookPos):
        dist = ((fishPos[0] - hookPos[0])**2) + ((fishPos[1] - hookPos[1])**2)
        return dist

    def mhDistance(self, fishPos, hookPos):
        xDist = abs(fishPos[0]-hookPos[0])
        yDist = abs(fishPos[1]-hookPos[1])
        
        if xDist > (20 - xDist):
            return (20 - xDist) + yDist
        else:
            return xDist + yDist


    def evaluate(self, currNode):
        fishCaught = currNode.state.get_caught()
        currScores = currNode.state.get_player_scores()
        fishScores = currNode.state.get_fish_scores()


        if fishCaught[0] is None:
            greenScore = self.fishDistanceValue(currNode, 0)
                        
        else:
            greenScore = fishScores[fishCaught[0]]
            # printD("TYPE TO SCORE: " + str(TYPE_TO_SCORE[fishCaught[0]]))
            # printD("Arrayen: " + str(fishScores[fishCaught[0]]))

        
        if fishCaught[1] is None:
            redScore = self.fishDistanceValue(currNode, 1)
        else:
            redScore = fishScores[fishCaught[1]]

        
        

        eval = currScores[0] + greenScore - currScores[1] - redScore
        return eval

    def fishDistanceValue(self, currNode, p):
        fishPos = currNode.state.get_fish_positions()
        hookPos = currNode.state.get_hook_positions()
        fishScores = currNode.state.get_fish_scores()
        player = "BLUE"
        if p == 0:
            player = "GREEN"
        else:
            player = "RED"
        dist = 0
        score = 0
        for fish in fishPos:
            if fishScores[fish] > 0:
                dist = self.euclDistance(fishPos[fish], hookPos[p])
                #if p == 0:
                #    print(player + " Fish pos: " + str(fishPos[fish]) + " Distance: " + str(dist))
                if dist == 0:	
                    scoreTemp = float('inf')	
                else:
                    #if p == 0:
                        #printD(player + " " + ACTION_TO_STR[currNode.move] + " Dist: " + str(dist))
                    scoreTemp = fishScores[fish]/(dist)
                if scoreTemp > score:
                    score = scoreTemp
        return score
    def search_best_next_move(self, currNode, depthLeft, alpha, beta, greenBoat):

        if time.time() - self.t >= 0.055:
            raise TimeoutError

        children = currNode.compute_and_get_children()
        children.sort(key=self.evaluate, reverse=True)
        
        if depthLeft == 0 or len(children) == 0:
            #printD("EVALUATE NODE:::: " + ACTION_TO_STR[currNode.move])
            eval = self.evaluate(currNode)
            if currNode is None:
                nextAct = 0
            else:
                nextAct = ACTION_TO_STR[currNode.move]
            return eval, nextAct

        if greenBoat:
            maxEval = float('-inf')
            nextAct = "stay"
            for child in children:
                eval, myAct= self.search_best_next_move(child, depthLeft - 1, alpha, beta, False)
                if eval > maxEval:
                    maxEval = eval
                    nextAct = myAct
                alpha = max(alpha, maxEval)
                if beta <= alpha:
                    break
            return maxEval, nextAct
        else:
            minEval = float('inf')
            nextAct = "stay"
            for child in children:
                eval, myAct = self.search_best_next_move(child, depthLeft - 1, alpha, beta, True)

                if eval < minEval:
                    minEval = eval
                    nextAct = myAct
                beta = min(minEval, beta)
                if beta <= alpha:
                    break
            return minEval, nextAct


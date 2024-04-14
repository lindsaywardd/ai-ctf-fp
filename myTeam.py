# myTeam.py

# ---------

# Licensing Information:  You are free to use or extend these projects for

# educational purposes provided that (1) you do not distribute or publish

# solutions, (2) you retain this notice, and (3) you provide clear

# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.

# 

# Attribution Information: The Pacman AI projects were developed at UC Berkeley.

# The core projects and autograders were primarily created by John DeNero

# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).

# Student side autograding was added by Brad Miller, Nick Hay, and

# Pieter Abbeel (pabbeel@cs.berkeley.edu).


from captureAgents import CaptureAgent

import distanceCalculator

import random, time, util, sys

from game import Directions

import game, capture

from util import nearestPoint


#################

# Team creation #

#################

# strat - maintain 1 pt lead & be defense otherwise

def createTeam(firstIndex, secondIndex, isRed,

               first='OffensiveReflexAgent', second='DefensiveReflexAgent'):
    """

    This function should return a list of two agents that will form the

    team, initialized using firstIndex and secondIndex as their agent

    index numbers.  isRed is True if the red team is being created, and

    will be False if the blue team is being created.



    As a potentially helpful development aid, this function can take

    additional string-valued keyword arguments ("first" and "second" are

    such arguments in the case of this function), which will come from

    the --redOpts and --blueOpts command-line arguments to capture.py.

    For the contest, however, your team will be created without

    any extra arguments, so you should make sure that the default

    behavior is what you want for the nightly contest.

    """

    # The following line is an example only; feel free to change it.

    return [eval(first)(firstIndex), eval(second)(secondIndex)]


##########

# Agents #

##########


class DummyAgent(CaptureAgent):
    """

    A Dummy agent to serve as an example of the necessary agent structure.

    You should look at baselineTeam.py for more details about how to

    create an agent as this is the bare minimum.

    """

    def registerInitialState(self, gameState: capture.GameState):
        """

        This method handles the initial setup of the

        agent to populate useful fields (such as what team

        we're on).



        A distanceCalculator instance caches the maze distances

        between each pair of positions, so your agents can use:

        self.distancer.getDistance(p1, p2)



        IMPORTANT: This method may run for at most 15 seconds.

        """

        '''
    
        Make sure you do not delete the following line. If you would like to
    
        use Manhattan distances instead of maze distances in order to save
    
        on initialization time, please take a look at
    
        CaptureAgent.registerInitialState in captureAgents.py.
    
        '''

        CaptureAgent.registerInitialState(self, gameState)

        '''
    
        Your initialization code goes here, if you need any.
    
        '''

        maxFood = self.getFood(gameState)


class ReflexCaptureAgent(CaptureAgent):
    """

    A base class for reflex agents that chooses score-maximizing actions

    """

    def registerInitialState(self, gameState: capture.GameState):

        maxFood = gameState.getBlueFood()

        self.start = gameState.getAgentPosition(self.index)

        CaptureAgent.registerInitialState(self, gameState)

    def chooseAction(self, gameState: capture.GameState):

        """

        Picks among the actions with the highest Q(s,a).

        """

        actions = gameState.getLegalActions(self.index)

        # You can profile your evaluation time by uncommenting these lines

        # start = time.time()

        values = [self.evaluate(gameState, a) for a in actions]

        # print('eval time for agent %d: %.4f' % (self.index, time.time() - start))

        maxValue = max(values)

        bestActions = [a for a, v in zip(actions, values) if v == maxValue]

        foodLeft = len(self.getFood(gameState).asList())

        if foodLeft <= 2:

            bestDist = 9999

            for action in actions:
                successor = self.getSuccessor(gameState, action)
                pos2 = successor.getAgentPosition(self.index)
                dist = self.getMazeDistance(self.start, pos2)

                if dist < bestDist:
                    bestAction = action
                    bestDist = dist
            return bestAction

        try:

            if self.getPreviousObservation().getAgentState(self.index).getPosition() == gameState.getAgentState(
                    self.index).getPosition():
                return random.choice(actions)

        except:

            print('cant access prior state')

        return random.choice(bestActions)

    def getSuccessor(self, gameState: capture.GameState, action):

        """

        Finds the next successor which is a grid position (location tuple).

        """

        successor = gameState.generateSuccessor(self.index, action)

        pos = successor.getAgentState(self.index).getPosition()

        if pos != nearestPoint(pos):

            # Only half a grid position was covered

            return successor.generateSuccessor(self.index, action)

        else:

            return successor

    def evaluate(self, gameState: capture.GameState, action):

        """

        Computes a linear combination of features and feature weights

        """

        features = self.getFeatures(gameState, action)

        weights = self.getWeights(gameState, action)

        return features * weights

    def getFeatures(self, gameState: capture.GameState, action):

        """

        Returns a counter of features for the state

        """

        features = util.Counter()

        successor = self.getSuccessor(gameState, action)

        features['successorScore'] = self.getScore(successor)

        return features

    def getWeights(self, gameState, action):

        """

        Normally, weights do not depend on the gamestate.  They can be either

        a counter or a dictionary.

        """

        return {'successorScore': 1.0}


class OffensiveReflexAgent(ReflexCaptureAgent):
    """

    A reflex agent that seeks food. This is an agent

    we give you to get an idea of what an offensive agent might look like,

    but it is by no means the best or only way to build an offensive agent.

    """

    def getFeatures(self, gameState: capture.GameState, action):

        # goes to defense when score is 1
        # numcarrying game
        #
        # successor = self.getSuccessor(gameState, action)
        # myState = successor.getAgentState(self.index)
        # if myState.numC

        if self.getScore(gameState) > 0:

            features = util.Counter()

            successor = self.getSuccessor(gameState, action)

            myState = successor.getAgentState(self.index)

            myPos = myState.getPosition()

            # Computes whether we're on defense (1) or offense (0)

            features['onDefense'] = 1

            if myState.isPacman:
                features['onDefense'] = 0

            # Computes distance to invaders
            enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
            invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
            features['numInvaders'] = len(invaders)

            if len(invaders) > 0:
                dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
                features['invaderDistance'] = min(dists)

            # gets the ghosts close to the broder so that they can attack the other team quickly
            if len(invaders) == 0:
                if myState.isPacman:
                    features['enemyTerritory'] = 1
                else:
                    features['enemyTerritory'] = 0
                    enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
                    chaser = [a for a in enemies if not a.isPacman and a.getPosition() != None]
                    if len(chaser) > 0:  # should always be greater than 0 as invaders is 0
                        dists = [self.getMazeDistance(myPos, a.getPosition()) for a in chaser]
                        features['chaserDistance'] = min(dists)

            if action == Directions.STOP: features['stop'] = 1

            rev = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction]

            if action == rev: features['reverse'] = 1

            # if features['chaserDistance'] >= 10:
            #     foodList = self.getFoodYouAreDefending(successor).asList()
            #     if len(foodList) > 0:
            #         myPos = successor.getAgentState(self.index).getPosition()
            #         minDistance = min([self.distancer.getDistance(myPos, food) for food in foodList])
            #         features['distanceToFood'] = minDistance


        else:
            successor = self.getSuccessor(gameState, action)

            myState = successor.getAgentState(self.index)

            x = len(self.getFoodYouAreDefending(gameState).asList())
            y = len(self.getFood(gameState).asList())
            # print(x, y)

            if x > y or myState.numCarrying > 0:
                features = util.Counter()
                successor = self.getSuccessor(gameState, action)
                foodList = self.getFoodYouAreDefending(successor).asList()
                features['successorScore'] = -len(foodList)
                if len(foodList) > 0:
                    myPos = successor.getAgentState(self.index).getPosition()
                    minDistance = min([self.distancer.getDistance(myPos, food) for food in foodList])
                    features['distanceToFood'] = minDistance
                return features

            #elif y <= x or myState.nummCarrying == 0:

            myPos = myState.getPosition()
            features = util.Counter()
            successor = self.getSuccessor(gameState, action)
            foodList = self.getFood(successor).asList()
            features['successorScore'] = -len(foodList)  # self.getScore(successor)
            enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
            chaser = [a for a in enemies if not a.isPacman and a.getPosition() != None]

            if len(chaser) > 0:
                dists = [self.getMazeDistance(myPos, a.getPosition()) for a in chaser]

                features['chaserDistance'] = 1 / (min(dists) ** 2)

            # Compute distance to the nearest food

            if len(foodList) > 0:
                myPos = successor.getAgentState(self.index).getPosition()

                x = [self.distancer.getDistance(myPos, food) for food in foodList]

                minDistance = min(x)

                x.remove(minDistance)

                secMinDistance = min(x)

                features['distanceToFood'] = minDistance

                features['secondMinDist'] = secMinDistance

        return features

    def getWeights(self, gameState: capture.GameState, action):

        successor = self.getSuccessor(gameState, action)

        enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]

        invaders = [a for a in enemies if a.isPacman and a.getPosition() is not None]
        #chasers = [a for a in enemies if not a.isPacman and a.getPosition() is not None]

        if self.getScore(gameState) > 0:
            if len(invaders) == 0:
                return {'numInvaders': -1000, 'onDefense': 100, 'invaderDistance': -5, 'chaserDistance': -5,
                        'stop': -100, 'reverse': -2, 'enemyTerritory': -180}

            else:

                return {'numInvaders': -1000, 'onDefense': 100, 'invaderDistance': -10, 'stop': -100, 'reverse': -2}

        return {'successorScore': 100, 'distanceToFood': -7, 'chaserDistance': -10, 'secondMinDistance': -3}


class DefensiveReflexAgent(ReflexCaptureAgent):
    """

      A reflex agent that keeps its side Pacman-free. Again,

      this is to give you an idea of what a defensive agent

      could be like.  It is not the best or only way to make

      such an agent.

    """

    def getFeatures(self, gameState: capture.GameState, action):

        features = util.Counter()

        successor = self.getSuccessor(gameState, action)

        myState = successor.getAgentState(self.index)

        myPos = myState.getPosition()

        # Computes whether we're on defense (1) or offense (0)

        features['onDefense'] = 1

        if myState.isPacman: features['onDefense'] = 0

        # Computes distance to invaders

        enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]

        invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]

        features['numInvaders'] = len(invaders)

        if len(invaders) > 0:
            dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]

            features['invaderDistance'] = min(dists)

        if len(invaders) == 0:

            if myState.isPacman:

                features['enemyTerritory'] = 1

            else:

                features['enemyTerritory'] = 0

                enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]

                chaser = [a for a in enemies if not a.isPacman and a.getPosition() != None]

                if len(chaser) > 0:  # should always be greater than 0 as invaders is 0

                    dists = [self.getMazeDistance(myPos, a.getPosition()) for a in chaser]

                    features['chaserDistance'] = max(dists)

        if action == Directions.STOP: features['stop'] = 1

        rev = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction]

        if action == rev: features['reverse'] = 1

        return features

    def getWeights(self, gameState: capture.GameState, action):

        return {'numInvaders': -1000, 'onDefense': 300, 'invaderDistance': -10, 'stop': -100, 'reverse': -2,
                'chaserDistance': -0.5}

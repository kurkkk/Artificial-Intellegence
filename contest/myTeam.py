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
import game
from util import nearestPoint
# from layout import width 
# from layout import height 
#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first = 'OffensiveReflexAgent', second = 'DefensiveReflexAgent'):
  """
  This function should return a list of two agents that will form the
  team, initialized using firstIndex and secondIndex as their agent
  index numbers.  isRed is True if the red team is being created, and
  will be False if the blue team is being created.

  As a potentially helpful development aid, this function can take
  additional string-valued keyword arguments ("first" and "second" are
  such arguments in the case of this function), which will come from
  the --redOpts and --blueOpts command-line arguments to capture.py.
  For the nightly contest, however, your team will be created without
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

  def registerInitialState(self, gameState):
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
    

    '''
    Your initialization code goes here, if you need any.
    '''
    #///////////////////////////////////////////////////////////////////////////////////////////////////
    self.start = gameState.getAgentPosition(self.index)
    self.bool = 1
    self.border = -1
    self.steps = 0
    self.foodchose = (-1,-1)
    self.findghost = 0
    self.borders = []
    self.foods = []
    self.getfood = 0
    self.ghostPos = None
    self.Capsulestime = 0
    self.haveCapsules = 0
    self.CapsulesPos = self.getCapsulesYouAreDefending(gameState)

    self.Capsules = len(self.CapsulesPos)
    self.invadersdist = -1
    self.fooddefend = []
    # self.width = width
    # self.height= height
    CaptureAgent.registerInitialState(self, gameState)
    #///////////////////////////////////////////////////////////////////////////////////////////////////


  def getSuccessor(self, gameState, action):
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

  def evaluate(self, gameState, action):
    """
    Computes a linear combination of features and feature weights
    """
    features = self.getFeatures(gameState, action)
    weights = self.getWeights(gameState, action)
    # print action
    # print features
    # print weights
    # print features * weights
    # time.sleep(0.1)
    return features * weights

  def getFeatures(self, gameState, action):
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

class OffensiveReflexAgent(DummyAgent):
  """
  A reflex agent that seeks food. This is an agent
  we give you to get an idea of what an offensive agent might look like,
  but it is by no means the best or only way to build an offensive agent.
  """
  def getFeatures(self, gameState, action):
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)
    myState = successor.getAgentState(self.index)
    myPos = myState.getPosition()
    mynowState = self.getCurrentObservation().getAgentState(self.index)
    # myPrevState = None
    # myPrevPos = (-1,-1)
    # if self.getPreviousObservation()!=None:
    #   myPrevState = self.getPreviousObservation().getAgentState(self.index)
    #   myPrevPos = myPrevState.getPosition()



    foodList = self.getFood(successor).asList()
    foodList += self.getCapsules(successor)    
    features['successorScore'] = -len(foodList)#self.getScore(successor)



    # Compute distance to the nearest food
    if  mynowState.isPacman:
      self.ghostPos = None
    if len(foodList) > 0: # This should always be True,  but better safe than sorry
      myPos = successor.getAgentState(self.index).getPosition()
      alldist = sorted([(self.getMazeDistance(myPos, food),food) for food in foodList])
      # print alldist
      # time.sleep(0.1)
      features['distanceToFood'] = alldist[0][0]
      if self.ghostPos != None and not mynowState.isPacman :
        
        print"find~~"
        
        direct = sorted([(abs(self.ghostPos[1]- d[1][1]),d) for d in alldist])
        direct.reverse()
        # print direct
        print "self.ghostPos",self.ghostPos,"d",direct[0][1][1]
        # time.sleep(0.5)
        features['distanceToFood'] = self.getMazeDistance(myPos, direct[0][1][1])

        # time.sleep(5)




      # if myPrevPos == myPos:
      #   features['distanceToFood'] += 5
    collides = 0
    defens = [successor.getAgentState(i) for i in self.getOpponents(successor)]
    ghost = [a for a in defens if  not a.isPacman and a.getPosition() != None]
    # features['numInvaders'] = len(ghost)
    if len(ghost) > 0:
      if not mynowState.isPacman:
        self.findghost = 2
        self.ghostPos =  ghost[0].getPosition()
      dists = [self.getMazeDistance(myPos, a.getPosition()) for a in ghost]
      features['ghostDistance'] = min(dists)
      print "features['ghostDistance']",features['ghostDistance']
      if features['ghostDistance'] <= 2:
        collides = 1
      else:
        collides = 0
    else:
      if self.findghost != 0:
        self.findghost -=0.5

    if (len(ghost) > 0 and mynowState.isPacman)or(self.steps >= 280 and mynowState.isPacman)or(self.findghost and not mynowState.isPacman)or (self.getfood>=5 and myPos not in foodList) or (self.getfood>=8) or (self.getScore(gameState)+self.getfood>=18):

      
      # time.sleep(2)
      print "back!!!!"
      features['backDistance'] = self.getMazeDistance(myPos, self.start)
    # time.sleep(0.5)
    # time.sleep(0.1)
    
    # print mynowState.getPosition()
    # time.sleep(0.02)
    # print tuple(map(int, mynowState.getPosition())) 
    # print self.CapsulesPos
    if self.Capsules and tuple(map(int, mynowState.getPosition())) in self.CapsulesPos:
      self.haveCapsules = 1
      self.Capsules -= 1
      self.Capsulestime = 40
    if self.haveCapsules :
      self.Capsulestime -=1
      # print features['ghostDistance']
      # time.sleep(10)
      if self.Capsulestime == 0 or collides:
        # time.sleep(5)
        self.haveCapsules = 0
      print "ok!"
      
      features['ghostDistance'] = 0
      if not (self.steps >= 280 and mynowState.isPacman):
        features['backDistance'] = 0
      # time.sleep(0.5)
    return features

  def getWeights(self, gameState, action):
    return {'successorScore': 111, 'distanceToFood': -1,'ghostDistance': 500,'backDistance':-588}




  def chooseAction(self, gameState):
    """
    Picks among actions randomly.
    """
    actions = gameState.getLegalActions(self.index)

    '''
    You should change this in your own agent.
    '''
    #///////////////////////////////////////////////////////////////////////////////////////////////////


    # You can profile your evaluation time by uncommenting these lines
    # start = time.time()

    actions.remove('Stop')
    values = [self.evaluate(gameState, a) for a in actions]
    # print 'eval time for agent %d: %.4f' % (self.index, time.time() - start)

    maxValue = max(values)
    bestActions = [a for a, v in zip(actions, values) if v == maxValue]

    foodLeft = len(self.getFood(gameState).asList())

    if foodLeft <= 2:
      bestDist = 9999
      for action in actions:
        successor = self.getSuccessor(gameState, action)
        pos2 = successor.getAgentPosition(self.index)
        dist = self.getMazeDistance(self.start,pos2)
        if dist < bestDist:
          bestAction = action
          bestDist = dist
      # print "bestActions:",bestActions
      return bestAction
    
    randomchoicebestActions = random.choice(bestActions)
    # print "randomchoicebestActions:", randomchoicebestActions

    successor = self.getSuccessor(gameState, randomchoicebestActions)
    myState = successor.getAgentState(self.index)
    mynowState = self.getCurrentObservation().getAgentState(self.index)
    foodList = self.getFood(successor).asList()    

    foodList += self.getCapsules(successor)


    if len(foodList) > 0: # This should always be True,  but better safe than sorry
      myPos = successor.getAgentState(self.index).getPosition()
      alldist = sorted([(self.getMazeDistance(myPos, food),food) for food in foodList])
      self.foodchose = alldist[0][1]
      # features['distanceToFood'] = minDistance
      # time.sleep(2)
    if myState.isPacman:
      if self.bool:
        self.bool = 0
        self.border = mynowState.getPosition()[0]
        print self.border
        self.foods = foodList
        # time.sleep(2)
    if mynowState.getPosition()[0] == self.border:
      self.borders.append(mynowState.getPosition())

    self.steps += 1
    if mynowState.getPosition() in self.foods:
      self.getfood += 1
      print self.getfood
      # time.sleep(0.5)
    if not mynowState.isPacman:
      self.getfood = 0
    return randomchoicebestActions





class DefensiveReflexAgent(DummyAgent):
  """
  A reflex agent that keeps its side Pacman-free. Again,
  this is to give you an idea of what a defensive agent
  could be like.  It is not the best or only way to make
  such an agent.
  """

  def getFeatures(self, gameState, action):
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)

    myState = successor.getAgentState(self.index)
    myPos = myState.getPosition()

    eatenfood = None
    foodList = self.getFoodYouAreDefending(successor).asList()
    foodList += self.getCapsulesYouAreDefending(successor)    
    if self.fooddefend != []:
      for food in self.fooddefend:
        if food not in foodList:
          print"eaten:",food
          # time.sleep(0.1)
          eatenfood = food 
    

    if eatenfood != None:
      self.getMazeDistance(myPos,eatenfood)
      print self.getMazeDistance(myPos,eatenfood)
      # time.sleep(2)
      features['distanceToeatenFood'] = self.getMazeDistance(myPos,eatenfood)
    if len(foodList) > 0: # This should always be True,  but better safe than sorry
      myPos = successor.getAgentState(self.index).getPosition()
      
      
      alldist = sorted([(food[0],self.getMazeDistance(myPos,food)) for food in foodList])
      alldist.reverse()

      # print gameState.getAgentPosition(4)
      # time.sleep(0.02)
      if len(foodList) >= 6:
        for i in range(6):
          features['distanceToFood'] += alldist[i][1]  

      

    # Computes whether we're on defense (1) or offense (0)
    features['onDefense'] = 1
    if myState.isPacman: features['onDefense'] = 0

    # Computes distance to invaders we can see
    enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]

    invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
    features['numInvaders'] = len(invaders)
    if action == Directions.STOP:
      features['stop'] = 1


    if len(invaders) > 0:
      dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
      features['invaderDistance'] = min(dists)
      if features['invaderDistance'] == self.invadersdist and features['invaderDistance']<=2 and action == Directions.STOP:
        features['stop'] = -1
        print "stop"
        # time.sleep(2)
      self.invadersdist = features['invaderDistance']



    rev = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction]
    if action == rev: features['reverse'] = 1



    print features
    # time.sleep(0.01)
    return features

  def getWeights(self, gameState, action):
    return {'numInvaders': -1000, 'onDefense': 100, 'invaderDistance': -111, 'stop': -100, 'reverse': -2,'distanceToFood':-5,'distanceToeatenFood':-55}

  def chooseAction(self, gameState):
    """
    Picks among actions randomly.
    """
    actions = gameState.getLegalActions(self.index)

    '''
    You should change this in your own agent.
    '''
    #///////////////////////////////////////////////////////////////////////////////////////////////////


    # You can profile your evaluation time by uncommenting these lines
    # start = time.time()
    values = [self.evaluate(gameState, a) for a in actions]
    # print 'eval time for agent %d: %.4f' % (self.index, time.time() - start)

    maxValue = max(values)
    bestActions = [a for a, v in zip(actions, values) if v == maxValue]

    foodLeft = len(self.getFood(gameState).asList())

    if foodLeft <= 2:
      bestDist = 9999
      for action in actions:
        successor = self.getSuccessor(gameState, action)
        pos2 = successor.getAgentPosition(self.index)
        dist = self.getMazeDistance(self.start,pos2)
        if dist < bestDist:
          bestAction = action
          bestDist = dist
      # print "bestActions:",bestActions
      return bestAction
    
    randomchoicebestActions = random.choice(bestActions)
    print "randomchoicebestActions:", randomchoicebestActions

    successor = self.getSuccessor(gameState, randomchoicebestActions)
    myState = successor.getAgentState(self.index)
    

    foodList = self.getFoodYouAreDefending(successor).asList()
    foodList += self.getCapsulesYouAreDefending(successor)    
    self.fooddefend = foodList

    # if myState.isPacman:
    #   if self.bool:
    #     self.bool = 0
    #     self.border = myState.getPosition()[0]
    #     print self.border
    #     print self.width
    #     print self.height
    #     time.sleep(5)

    self.steps += 1
    return randomchoicebestActions
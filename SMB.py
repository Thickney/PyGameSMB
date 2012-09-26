import pygame
import sys
from pygame.locals import *

####################################
# Constants
####################################

red = [255,0,0]
green = [0,255,0]
blue = [0,0,255]
white = [255,255,255]
black = [0,0,0]

####################################
# Classes
####################################

# Entity
class Entity:
    x = 0
    y = 0
    w = 0
    h = 0
    rect = Rect(x,y,w,h)
    color = [0,0,0]
    direction = "right"
    currState = None
    prevState = None
        
    def __init__ (self, x, y, w, h, color):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.color = color
        self.rect = Rect(x,y,w,h)
        self.allStates = {}

    def translate (self, dx, dy):
        if dx < 0:
            self.direction = "left"
        elif dx > 0:
            self.direction = "right"

        self.x += dx
        self.y += dy
        self.rect = Rect(self.x,self.y,self.w,self.h)

    def changeState (self, stateID):
        if self.allStates.get(stateID) is None:
            return
        else:
            self.newState = self.allStates.get(stateID)
            self.currState.exitState(self)
            self.prevState = self.currState
            self.currState = self.newState
            self.currState.enterState(self)

    def draw (self):
        pygame.draw.rect(screen, self.color, [self.x,self.y,self.w,self.h], 6)

# Coin
class Coin (Entity):
    def __init__ (self, x, y, w, h, color):
        Entity.__init__(self, x, y, w, h, color)
        self.allStates = { "idle":CoinStateIdle() }

    def update (self, deltaTime):
        self.currState.execute(self, deltaTime)    

# BrickBlock
class BrickBlock (Entity):
    def __init__ (self, x, y, w, h, color):
        Entity.__init__(self, x, y, w, h, color)
        self.allStates = { "idle":BrickBlockStateIdle(), "hit_light":BrickBlockStateHitLight(), "hit_hard":BrickBlockStateHitHard() }   

    def update (self, deltaTime):
        self.currState.execute(self, deltaTime)

# QuestionBlock
class QuestionBlock (Entity):
    def __init__ (self, x, y, w, h, color):
        Entity.__init__(self, x, y, w, h, color)
        self.allStates = { "idle":QuestionBlockStateIdle(), "hit":QuestionBlockStateHit() }   

    def update (self, deltaTime):
        self.currState.execute(self, deltaTime)

# GroundBlock 
class GroundBlock (Entity):
    def __init__ (self, x, y, w, h, color):
        Entity.__init__(self, x, y, w, h, color)
        self.allStates = { "idle":GroundBlockStateIdle() }   

    def update (self, deltaTime):
        self.currState.execute(self, deltaTime)

# Mushroom
class Mushroom (Entity):
    def __init__ (self, x, y, w, h, color):
        Entity.__init__(self, x, y, w, h, color)
        self.allStates = { "spawn":MushroomStateSpawn(), "move":MushroomStateMove() }

    def update (self, deltaTime):
        self.currState.execute(self, deltaTime)

# Goomba
class Goomba (Entity):
    def __init__ (self, x, y, w, h, color):
        Entity.__init__(self, x, y, w, h, color)
        self.allStates = { "move":GoombaStateMove(), "fall":GoombaStateFall(), "hit":GoombaStateHit(), "squished":GoombaStateSquished() }

    def update (self, deltaTime):
        self.currState.execute(self, deltaTime)

# Mario
class Mario (Entity):
    def __init__ (self, x, y, w, h, color):
        Entity.__init__(self, x, y, w, h, color)
        self.allStates = { "idle":MarioStateIdle(), "move":MarioStateMove(), "run":MarioStateRun(), "jump":MarioStateJump() }
        self.prevState = self.allStates.get("idle")
        self.currState = self.prevState
        self.speed = 0.5
        self.isDead = False
        self.dy = 0
        self.jumpHeight = 2
        self.velocity = 0
        
    def update (self, deltaTime):
        self.currState.execute(self, deltaTime)


# State
class State:

    def enterState (self, entity):
        raise NotImplementedError("Please Implement enter() in State subclass.")

    def execute (self, entity, deltaTime):
        raise NotImplementedError("Please Implement execute() in State subclass.")

    def exitState (self, entity):
        raise NotImplementedError("Please Implement exit() in State subclass.")

    def toString (self):
        raise NotImplementedError("Please Implement toString() in State subclass.")

# MarioStateIdle
class MarioStateIdle (State):

    def enterState (self, entity):
        print "Entering Mario Idle."

    def execute (self, entity, deltaTime):
        key = pygame.key.get_pressed()
        if key[K_SPACE]:
            entity.changeState("jump")
        elif key[K_a]:
            entity.direction = "left"
            entity.changeState("move")
        elif key[K_d]:
            entity.direction = "right"
            entity.changeState("move")

    def exitState (self, entity):
        print "Exiting Mario Idle."

    def toString (self):
        return "idle"

# MarioStateMove
class MarioStateMove (State):

    def enterState (self, entity):
        print "Entering Mario Move."

    def execute (self, entity, deltaTime):
        key = pygame.key.get_pressed()
        if key[K_LSHIFT]:
            mario.changeState("run")
            
        if key[K_a]:
            mario.translate(-(mario.speed) * deltaTime, 0)
            mario.direction = "left"
            
        if key[K_d]:
            mario.translate(mario.speed * deltaTime, 0)
            mario.direction = "right"

        if not key[K_a] and not key[K_d]:
            mario.changeState("idle")
 
    def exitState (self, entity):
        print "Exiting Mario Move."

    def toString (self):
        return "move"

# MarioStateRun
class MarioStateRun (State):

    def enterState (self, entity):
        print "Entering Mario Run."

    def execute (self, entity, deltaTime):
        key = pygame.key.get_pressed()

        # Check if player stopped running.
        if not key[K_LSHIFT]:
            if not key[K_a] and not key[K_d]:
                mario.changeState("idle")
            if key[K_a]:
                mario.direction = "left"
                mario.changeState("move")
            if key[K_d]:
                mario.direction = "right"
                mario.changeState("move")

        # Still running.
        else:
            if key[K_a]:
                mario.translate(-(mario.speed) * deltaTime * 2, 0)
                mario.direction = "left"
                
            if key[K_d]:
                mario.translate(mario.speed * deltaTime * 2, 0)
                mario.direction = "right"
 
    def exitState (self, entity):
        print "Exiting Mario Run."

    def toString (self):
        return "run"

# MarioStateJump
class MarioStateJump (State):
    
    def enterState (self, entity):
        print "Entering Mario Jump."
        mario.velocity = 0
        self.startHeight = mario.y

    def execute (self, entity, deltaTime):
        key = pygame.key.get_pressed()

        # Update upward velocity.
        mario.dy += mario.velocity
        mario.velocity += gravity

        # Start falling back down.
        if mario.y < self.startHeight - mario.jumpHeight:
            mario.velocity *= -0.95;

        mario.translate(0, mario.velocity * deltaTime)

        # Landed.
        if mario.y >= groundY:
            mario.changeState("idle")

    def exitState (self, entity):
        print "Exiting Mario Jump."

    def toString (self):
        return "jump"


# GroundBlockStateIdle
class GroundBlockStateIdle (State):
    def enterState (self, entity):
        return

    #def execute (self, entity, deltaTime):
    #    if entity.rect.collideRect(mario.rect):
            # Take mario's prev and curr positions and
            # decide which side of the ground block to push
            # mario away from.

    def exitState(self, entity):
        return

    def toString (self):
        return "idle"

# CoinStateIdle
class CoinStateIdle (State):
    def enterState (self, entity):
       return

    def execute (self, entity, deltaTime):
        return

    def exitState(self, entity):
        return

    def toString (self):
        return "idle"

####################################
# Levels
####################################

# Level
class Level:
    def __init__ (self, fileHandle):
        self.f = open(fileHandle)
        self.tileRows = self.f.readlines()

        # Set up dummy tile
        self.map = []

        i = 0
        for row in self.tileRows:
            j = 0
            for tile in row:
                self.loadItem(tile, j, i)
                j += 1
            i += 1

    def loadItem (self, tile, x, y):
        xPos = x * tileWidth
        yPos = y * tileWidth

        if (tile == blankTile):
            return
        
        elif (tile == groundTile):
            self.map.append(GroundBlock(xPos, yPos, tileWidth, tileWidth, black))

        elif (tile == marioTile):
            self.map.append(Mario(xPos, yPos, tileWidth, tileWidth, marioColor))

    def getMario (self):
        for tile in self.map:
            if tile.color == marioColor:
                return tile
        return None

    def draw (self):
        for tile in self.map:
            pygame.draw.rect(screen, tile.color, [tile.x, tile.y, tile.w, tile.h], 6)


# 1-1
class LevelOneOne (Level):
    def __init__ (self, fileHandle):
        Level.__init__(self, fileHandle)

    def update (self, deltaTime):
        # Handle stuff like trigger zones and where/when
        # enemies should spawn.
        return


####################################
# Globals
####################################

# Display
pygame.init()
screenSize = [1280,720]
screenBGColor = white

# Tiles
tileWidth = 40
blankTile = ' '
groundTile = 'g'
marioTile = 'm'
marioColor = blue

# Levels
levelHandle = "1-1.txt"
level = LevelOneOne(levelHandle)

# Mario
groundY = screenSize[1] - 50
gravity = 0.1

# Game
screen = pygame.display.set_mode(screenSize)
pygame.display.set_caption("SMB")
clock = pygame.time.Clock()
running = True


####################################
# Functions
####################################

def render ():
    screen.fill(screenBGColor)
        
    level.draw()

    pygame.display.flip()

def tick ():
    deltaTime = clock.tick(60)

    mario = level.getMario()
    if not mario is None:
        mario.update(deltaTime)

####################################
# Main loop
####################################

while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        if event.type == KEYDOWN and event.key == K_ESCAPE:
            running = False

    tick()
    render()

    mario = level.getMario()
    if not mario is None and mario.isDead:
        print "Game Over"
        running = False

pygame.quit()




















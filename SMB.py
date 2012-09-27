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

# Camera
class Camera:
    def __init__ (self):
        self.getValues()

    def update (self):
        self.getValues()

    def getValues (self):
        if level.getMario().x < screenSize[0]/2:
            self.x = 0
        else:
            self.x = screenSize[0]/2 - tileWidth/2

        self.y = 0
        self.width = screenSize[0]
        self.height = screenSize[1]

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
        self.collidingObjects = []
        self.hasCollision = False

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

    def addCollision (self, collided):
        self.collidingObjects.append(collided)
        self.hasCollision = True

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
        self.allStates = { "idle":BrickBlockStateIdle() } #, "hit_light":BrickBlockStateHitLight(), "hit_hard":BrickBlockStateHitHard() }   
        self.prevState = self.allStates.get("idle")
        self.currState = self.prevState
        
    def update (self, deltaTime):
        self.currState.execute(self, deltaTime)

# QuestionBlock
class QuestionBlock (Entity):
    def __init__ (self, x, y, w, h, color):
        Entity.__init__(self, x, y, w, h, color)
        self.allStates = { "idle":QuestionBlockStateIdle() } #, "hit":QuestionBlockStateHit() }
        self.prevState = self.allStates.get("idle")
        self.currState = self.prevState

    def update (self, deltaTime):
        self.currState.execute(self, deltaTime)

# GroundBlock 
class GroundBlock (Entity):
    def __init__ (self, x, y, w, h, color):
        Entity.__init__(self, x, y, w, h, color)
        self.allStates = { "idle":GroundBlockStateIdle() }
        self.prevState = self.allStates.get("idle")
        self.currState = self.prevState

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
        self.allStates = { "idle":MarioStateIdle(), "move":MarioStateMove(), "jump":MarioStateJump(), "fall":MarioStateFall() }
        self.prevState = self.allStates.get("idle")
        self.currState = self.prevState
        self.speed = 0.5
        self.isDead = False
        self.dy = 0
        self.jumpHeight = 150
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
        return

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
        return
    
    def toString (self):
        return "idle"

# MarioStateMove
class MarioStateMove (State):
    def enterState (self, entity):
        self.run = False
    
    def execute (self, entity, deltaTime):
        key = pygame.key.get_pressed()

        # Check for move off of any platform
        downRect = entity.rect
        downRect.y += 10
        shouldFall = True
        for item in level.map:
            if item != mario and downRect.colliderect(item):
                shouldFall = False

        if shouldFall:
            entity.changeState("fall")

        if key[K_SPACE]:
            entity.changeState("jump")
        
        if key[K_LSHIFT]:
            self.run = True
            
        if key[K_a]:
            if self.run:
                mario.translate(-(mario.speed) * 2 * deltaTime, 0)
            else:
                mario.translate(-(mario.speed) * deltaTime, 0)
            mario.direction = "left"
            
        if key[K_d]:
            if self.run:
                mario.translate(mario.speed * 2 * deltaTime, 0)
            else:
                mario.translate(mario.speed * deltaTime, 0)
            mario.direction = "right"

        if not key[K_LSHIFT]:
            self.run = False

        if not key[K_a] and not key[K_d]:
            mario.changeState("idle")
 
    def exitState (self, entity):
        return
    
    def toString (self):
        return "move"

# MarioStateJump
class MarioStateJump (State):
    def enterState (self, entity):
        entity.dy = 0
        entity.velocity = -0.2
        self.startHeight = entity.y
        self.dx = 0

    def execute (self, entity, deltaTime):
        # Check in-air movement.
        key = pygame.key.get_pressed()

        if key[K_a]:
            entity.direction = "left"
            self.dx = -(entity.speed)
        if key[K_d]:
            entity.direction = "right"
            self.dx = entity.speed
        
        # Update upward velocity.
        entity.dy += entity.velocity
        entity.velocity += gravity

        # Start falling back down.
        if entity.velocity >= 0:
            entity.changeState("fall")
        else:
            entity.translate(self.dx * deltaTime, entity.dy * deltaTime)

    def exitState (self, entity):
        return
    
    def toString (self):
        return "jump"

# MarioStateFall
class MarioStateFall (State):
    def enterState (self, entity):
        self.dx = 0
    
    def execute (self, entity, deltaTime):
        # Check in-air movement.
        key = pygame.key.get_pressed()

        if key[K_a]:
            entity.direction = "left"
            self.dx = -(entity.speed)
        if key[K_d]:
            entity.direction = "right"
            self.dx = entity.speed

        # Check if any collisions.
        if (entity.hasCollision):
            for obj in entity.collidingObjects:
                if isinstance(obj, GroundBlock) or isinstance(obj, BrickBlock):
                    entity.changeState("idle")
                    # Place entity on top of obj.
                    entity.translate(0, obj.y - entity.y - entity.h)

            entity.hasCollision = False
            entity.collidingObjects = []
            return

        if entity.dy > maxVelocity:
            entity.dy = maxVelocity
        else:
            entity.dy += entity.velocity
            
        entity.velocity += gravity
        entity.translate(self.dx * deltaTime, entity.dy * deltaTime)

    def exitState (self, entity):
        return
    def toString (self):
        return "fall"

# QuestionBlockStateIdle
class QuestionBlockStateIdle (State):
    def enterState (self, entity):
        return

    def execute (self, entity, deltaTime):
        return

    def exitState(self, entity):
        return

    def toString (self):
        return "idle"

# BrickBlockStateIdle
class BrickBlockStateIdle (State):
    def enterState (self, entity):
        return

    def execute (self, entity, deltaTime):
        return

    def exitState(self, entity):
        return

    def toString (self):
        return "idle"

# GroundBlockStateIdle
class GroundBlockStateIdle (State):
    def enterState (self, entity):
        return

    def execute (self, entity, deltaTime):
        return
        
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

        elif (tile == blockTile):
            self.map.append(BrickBlock(xPos, yPos, tileWidth, tileWidth, red))

        elif (tile == questionTile):
            self.map.append(QuestionBlock(xPos, yPos, tileWidth, tileWidth, green))

    def update (self, deltaTime):
        for tile in self.map:
            tile.update(deltaTime)
        
        self.checkCollisions()

    def checkCollisions (self):
        mario = self.getMario()
        for tile in self.map:
            if tile != mario and tile.rect.colliderect(mario.rect):
                    tile.addCollision(mario)
                    mario.addCollision(tile)

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
        Level.update(self, deltaTime)
        
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
pipeTile = 'p'
blockTile = 'b'
questionTile = 'q'
marioColor = blue

# Levels
levelHandle = "1-1.txt"
level = LevelOneOne(levelHandle)

# Physics
gravity = 0.02
maxVelocity = 1

# Game
screen = pygame.display.set_mode(screenSize)
pygame.display.set_caption("SMB")
camera = Camera()
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
    level.update(deltaTime)
    camera.update()
    

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




















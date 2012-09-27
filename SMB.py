import pygame
import sys
from pygame.locals import *

####################################
# Constants
####################################

red = [255,0,0]
green = [0,255,0]
blue = [0,0,255]
lightBlue = [135,206,250]
white = [255,255,255]
black = [0,0,0]
gold = [255,215,0]
groundBrown = [160,82,45]
brickBrown = [205,133,63]

marioColor = white

####################################
# Classes
####################################

# Camera
class Camera:
    def __init__ (self):
        self.getValues()
        self.x = 0
        self.y = 0
        self.w = screenSize[0]
        self.h = screenSize[1]

    def update (self):
        self.getValues()

    def getValues (self):
        mario = level.getMario()
        if mario is None:
            return
        if mario.x < screenSize[0]/2:
            self.x = 0
        else:
            self.x = level.getMario().x - screenSize[0]/2 + tileWidth/2

# Struct
class Struct (object):
    def __init__ (self, **entries):
        self.__dict__.update(entries)

# Entity
class Entity (object):
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

    def left (self):
        return self.x
    def right (self):
        return self.x + self.w
    def bottom (self):
        return self.y + self.h
    def top (self):
        return self.y

    def translate (self, dx, dy):
        if dx < 0:
            self.direction = "left"
        elif dx > 0:
            self.direction = "right"

        self.x += dx

        if isinstance(self, Mario) and self.x < 0:
            self.x = 0
        
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
        pygame.draw.rect(screen, self.color, [self.x - camera.x, self.y - camera.y, self.w, self.h], 0)

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

# Pipe
class Pipe (Entity):
    def __init__ (self, x, y, w, h, color):
        Entity.__init__(self, x, y, w, h, color)
        self.allStates = { "idle":PipeStateIdle() }
        self.prevState = self.allStates.get("idle")
        self.currState = self.prevState

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
class State (object):

    def enterState (self, entity):
        raise NotImplementedError("Please Implement enter() in State subclass.")

    def execute (self, entity, deltaTime):
        raise NotImplementedError("Please Implement execute() in State subclass.")

    def exitState (self, entity):
        raise NotImplementedError("Please Implement exit() in State subclass.")

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

# MarioStateMove
class MarioStateMove (State):
    def enterState (self, entity):
        self.run = False
    
    def execute (self, entity, deltaTime):
        key = pygame.key.get_pressed()

        # Check for move into a wall
        if entity.hasCollision:
            for tile in entity.collidingObjects:
                sides = collision_sides(entity, tile)
                if sides.left:
                    entity.x = tile.x + tile.w
                elif sides.right:
                    entity.x = tile.x - entity.w

        # Check for move off of any platform
        downRect = entity.rect
        downRect.y += 10
        shouldFall = True
        for item in level.map:
            if item != entity and downRect.colliderect(item):
                shouldFall = False

        if shouldFall:
            entity.changeState("fall")

        if key[K_SPACE]:
            entity.changeState("jump")
        
        if key[K_LSHIFT]:
            self.run = True
            
        if key[K_a]:
            if self.run:
                entity.translate(-(entity.speed) * 2 * deltaTime, 0)
            else:
                entity.translate(-(entity.speed) * deltaTime, 0)
            entity.direction = "left"
            
        if key[K_d]:
            if self.run:
                entity.translate(entity.speed * 2 * deltaTime, 0)
            else:
                entity.translate(entity.speed * deltaTime, 0)
            entity.direction = "right"

        if not key[K_LSHIFT]:
            self.run = False

        if not key[K_a] and not key[K_d]:
            entity.changeState("idle")
 
    def exitState (self, entity):
        return

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
        speed = entity.speed
        jumpGravity = gravity

        if key[K_LSHIFT]:
            speed *= 2
            jumpGravity *= 0.9
        if key[K_a]:
            entity.direction = "left"
            self.dx = -speed
        if key[K_d]:
            entity.direction = "right"
            self.dx = speed

        rect = Rect(entity.x, entity.y - entity.w/3, entity.w, entity.h)
        for tile in level.map:
            if not isinstance(tile, Mario) and rect.colliderect(tile.rect):
                entity.translate(0, entity.y - tile.y + entity.h)
                entity.changeState("fall")
                return
        
        # Update upward velocity.
        entity.dy += entity.velocity
        entity.velocity += jumpGravity

        # Start falling back down.
        if entity.velocity >= 0:
            entity.changeState("fall")
        else:
            entity.translate(self.dx * deltaTime, entity.dy * deltaTime)

    def exitState (self, entity):
        return
    

# MarioStateFall
class MarioStateFall (State):
    def enterState (self, entity):
        self.dx = 0
    
    def execute (self, entity, deltaTime):
        # Check in-air movement.
        key = pygame.key.get_pressed()
        speed = entity.speed

        if key[K_LSHIFT]:
            speed *= 2
        if key[K_a]:
            entity.direction = "left"
            self.dx = -speed
        if key[K_d]:
            entity.direction = "right"
            self.dx = speed

        rect = Rect(entity.x, entity.y + 10, entity.w, entity.h)
        for tile in level.map:
            if not isinstance(tile, Mario) and rect.colliderect(tile.rect):
                entity.changeState("idle")
                entity.translate(0, tile.y - entity.y - entity.h)
                return

        if entity.dy > maxVelocity:
            entity.dy = maxVelocity
        else:
            entity.dy += entity.velocity
            
        entity.velocity += gravity
        entity.translate(self.dx * deltaTime, entity.dy * deltaTime)

    def exitState (self, entity):
        return

# QuestionBlockStateIdle
class QuestionBlockStateIdle (State):
    def enterState (self, entity):
        return

    def execute (self, entity, deltaTime):
        return

    def exitState(self, entity):
        return

# BrickBlockStateIdle
class BrickBlockStateIdle (State):
    def enterState (self, entity):
        return

    def execute (self, entity, deltaTime):
        return

    def exitState(self, entity):
        return

# GroundBlockStateIdle
class GroundBlockStateIdle (State):
    def enterState (self, entity):
        return

    def execute (self, entity, deltaTime):
        return
        
    def exitState(self, entity):
        return

# PipeStateIdle
class PipeStateIdle (State):
    def enterState (self, entity):
        return

    def execute (self, entity, deltaTime):
        return
        
    def exitState(self, entity):
        return

# CoinStateIdle
class CoinStateIdle (State):
    def enterState (self, entity):
       return

    def execute (self, entity, deltaTime):
        return

    def exitState(self, entity):
        return

####################################
# Levels
####################################

# Level
class Level:
    
    def __init__ (self, fileHandle):
        self.f = open(fileHandle)
        self.tileRows = self.f.readlines()
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
            self.map.append(GroundBlock(xPos, yPos, tileWidth, tileWidth, groundBrown))

        elif (tile == marioTile):
            self.map.append(Mario(xPos, yPos, tileWidth, tileWidth, white))

        elif (tile == blockTile):
            self.map.append(BrickBlock(xPos, yPos, tileWidth, tileWidth, brickBrown))

        elif (tile == questionTile):
            self.map.append(QuestionBlock(xPos, yPos, tileWidth, tileWidth, gold))

        elif (tile == pipeTile):
            self.map.append(Pipe(xPos, yPos, tileWidth, tileWidth, green))

    def update (self, deltaTime):
        for tile in self.map:
            tile.update(deltaTime)
        
        self.checkCollisions()

    def checkCollisions (self):
        mario = self.getMario()
        if mario is None:
            return
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
            tile.draw()

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
screenBGColor = lightBlue

# Tiles
tileWidth = 50
blankTile = ' '
groundTile = 'g'
marioTile = 'm'
pipeTile = 'p'
blockTile = 'b'
questionTile = 'q'

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

def collision_sides (a, b):
    sides = Struct(left=False, right=False, top=False, bottom=False)
    
    left = Rect(a.left(), a.top() + 1, 1, a.h - 2)
    right = Rect(a.right(), a.top() + 1, 1, a.h - 2)
    top = Rect(a.left() + 1, a.top(), a.w - 2, 1)
    bottom = Rect(a.left() + 1, a.bottom(), a.w - 2, 1)

    if left.colliderect(b):
        sides.left = True
    if right.colliderect(b):
        sides.right = True
    if top.colliderect(b):
        sides.top = True
    if bottom.colliderect(b):
        sides.bottom = True

    return sides

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
    #if not mario is None and mario.isDead:
    if not mario is None and mario.y > screenSize[1]:
        print "Game Over"
        running = False

pygame.quit()




















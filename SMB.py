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


####################################
# Globals
####################################

pygame.init()
screenSize = [1280,720]
screenBGColor = white

screen = pygame.display.set_mode(screenSize)
pygame.display.set_caption("SMB")

mario = Mario(screenSize[0]/2, screenSize[1]/2, 50, 50, blue)
groundY = screenSize[1] - 50
gravity = 0.1

clock = pygame.time.Clock()
running = True


####################################
# Functions
####################################

def render ():
    screen.fill(screenBGColor)
    mario.draw()
    pygame.display.flip()

def tick ():
    deltaTime = clock.tick(60)
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

    if mario.isDead:
        print "Game Over"
        running = False

pygame.quit()




















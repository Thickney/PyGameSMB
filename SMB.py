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
        if allStates.get(stateID) is None:
            return
        else:
            newState = allStates.get(stateID)
            self.currState.exit(self)
            self.prevState = self.currState
            self.currState = self.newState
            self.currState.enter(self)

    def draw (self):
        pygame.draw.rect(screen, self.color, [self.x,self.y,self.w,self.h], 6)
        

# Mario
class Mario (Entity):
    
    def __init__ (self, x, y, w, h, color):
        Entity.__init__(self, x, y, w, h, color)
        self.allStates = { "idle":MarioStateIdle(), "move":MarioStateMove() }
        self.prevState = self.allStates.get("idle")
        self.currState = self.prevState
        self.speed = 1
        
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
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_a:
                    direction = "left"
                    changeState("move")
                    
                elif event.key == K_d:
                    direction = "right"
                    changeState("move")
            else:
                changeState("idle")

    def exitState (self, entity):
        print "Exiting Mario Idle."

    def toString (self):
        return "idle"

# MarioStateMove
class MarioStateMove (State):

    def enterState (self, entity):
        print "Entering Mario Idle."

    def execute (self, entity, deltaTime):
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_a:
                    direction = "left"
                    entity.translate(-1, 0)
                    
                elif event.key == K_d:
                    direction = "right"
                    entity.translate(1, 0)
            else:
                changeState("idle")

    def exitState (self, entity):
        print "Exiting Mario Idle."

    def toString (self):
        return "move"


####################################
# Globals
####################################

pygame.init()
screenSize = [1280,720]
screenBGColor = white
deltaTime = 0

screen = pygame.display.set_mode(screenSize)
pygame.display.set_caption("SMB")

mario = Mario(screenSize[0]/2, screenSize[1]/2, 50, 50, blue)

clock = pygame.time.Clock()
running = True

####################################
# Functions
####################################

def render ():
    screen.fill(screenBGColor)
    deltaTime = clock.tick(60)
    mario.draw()
    
    pygame.display.flip()

def tick ():
    mario.update(deltaTime)

####################################
# Main loop
####################################

while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
            
    tick()
    render()

pygame.quit()




















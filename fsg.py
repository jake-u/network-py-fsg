# v3/18 12:16

import sys
import copy
import functools
import random
import socket
import struct

import numpy

if 'numpy' not in sys.modules:
  print(f"the python module \'numpy\' is not installed.")
  exit()

import pygame

if 'pygame' not in sys.modules:
  print(f"the module \'pygame\' is not installed.")
  exit()

random.seed(5)

def buildCoordScreens(w, h, count=8):
  coordScreens = []

  for c in range(count):
    coordScreen = []
    for x in range(w):
      for y in range(h):
        coordScreen.append((x, y))
    
    candidate = copy.deepcopy(coordScreen)
    random.shuffle(candidate)
    coordScreens.append(candidate)

  random.seed(5)
  return coordScreens

grad = 0
simgrad = 0
def getChaosColor():
  global grad
  grad %= 1536

  """
  0-256 : R & g+
  256-512 : r- & G
  512-768 : G & b+
  768-1024 : g- & B
  1024-1280 : r+ & B
  1280-1536 : R & b-
  """

  red = 0
  green = 0
  blue = 0

  # full static
  if (grad >= 0 and grad < 256) or (grad >= 1280 and grad < 1536):
    red = 255
  if (grad >= 256 and grad < 768):
    green = 255
  if (grad >= 768 and grad < 1280):
    blue = 255

  # inc
  if (grad >= 0 and grad < 256):
    green = grad
  if (grad >= 512 and grad < 768):
    blue = grad - 512
  if (grad >= 1024 and grad < 1280):
    red = grad - 1024

  # dec
  if (grad >= 256 and grad < 512):
    red = 255 - (grad - 256)
  if (grad >= 768 and grad < 1024):
    green = 255 - (grad - 768)
  if (grad >= 1280 and grad < 1536):
    blue = 255 - (grad - 1280)

  color = 0
  color += red * 0x10000
  color += green * 0x100
  color += blue

  return color

def getColor(p):
    match p:
      case Particle.NULL:
        return 0xFFFFFF
      case Particle.SAND:
        return 0xC3B080
      case Particle.WATER:
        return 0x0E5D9D
      case Particle.FIRE:
        return 0xFE7E19
      case Particle.WOOD:
        return 0xB98D64
      case Particle.WALL:
        return 0x888888
      case Particle.ACID:
        return 0xA9FC03
      case Particle.GASOLINE:
        return 0xF4E62A
      case Particle.STONE:
        return 0xB6B19D
      case Particle.LAVA:
        return 0xD01122
      case Particle.VIRUS:
        return 0x880088
      case Particle.CHAOS:
        return getChaosColor()
      case Particle.PLATINUM:
        return 0xE4E4E4
      case Particle.NAPALM:
        return 0x774411
      case Particle.VINE:
        return 0x00BB00
      case Particle.CLONER:
        return 0x907010
      case _:
        return 0xFF00FF # should not happen, bright pink and noticible

class Particle:
  NULL = -1 # effectively a particle that does not exist
  SAND = 0
  WATER = 1
  FIRE = 2
  WOOD = 3
  WALL = 4
  ACID = 5
  GASOLINE = 6
  STONE = 7
  LAVA = 8
  VIRUS = 9
  CHAOS = 10
  PLATINUM = 11
  NAPALM = 12
  VINE = 13
  CLONER = 14

class FSG:
  def __init__(self, width, height):
    self.particles = numpy.full((width, height), Particle.NULL)
    self.width = width
    self.height = height
    self.coords = buildCoordScreens(width, height)

    self.rngState = 4
  
  def randomBool(self):
    #return (self.rngState % 2) == 1
    return random.randint(0, 1) == 1
  
  def randomThree(self):
    """
    self.rngState += 2
    return (self.rngState % 3) - 1
    """
    return random.randint(-1, 1)

  def clampX(self, x):
    return max(0, min(x, self.width - 1))
  
  def clampY(self, y):
    return max(0, min(y, self.height - 1))
  
  def clampView(self, x, y):
    return self.particles[self.clampX(x)][self.clampY(y)]
  
  def clampViewSet(self, x, y, pt):
    self.particles[self.clampX(x)][self.clampY(y)] = pt

  def update(self):
    #self.rngState += 17
    for (x, y) in self.coords[random.randrange(0, len(self.coords) - 1)]:
      match self.particles[x][y]:
        case Particle.NULL:
          continue
        case Particle.WOOD:
          continue
        case Particle.WALL:
          continue
        case Particle.SAND:
          self.uptSand(x, y)
          continue
        case Particle.WATER:
          self.uptWater(x, y)
          continue
        case Particle.FIRE:
          self.uptFire(x, y)
          continue
        case Particle.ACID:
          self.uptAcid(x, y)
          continue
        case Particle.GASOLINE:
          self.uptGasoline(x, y)
          continue
        case Particle.STONE:
          self.uptStone(x, y)
          continue
        case Particle.LAVA:
          self.uptLava(x, y)
          continue
        case Particle.VIRUS:
          self.uptVirus(x, y)
          continue
        case Particle.CHAOS:
          self.uptChaos(x, y)
          continue
        case Particle.PLATINUM:
          continue
        case Particle.NAPALM:
          self.uptNapalm(x, y)
          continue
        case Particle.VINE:
          self.uptVine(x, y)
          continue
        case Particle.CLONER:
          self.uptCloner(x, y)
          continue
          
  
  def uptSand(self, x, y):
    self.uptPowder(x, y, Particle.SAND)

  def uptWater(self, x, y):
    for i in range(6):
      self.randomTouch(x, y, [Particle.FIRE], Particle.NULL)
      candidateX = self.clampX(self.randomThree() + x)
      candidateY = self.clampY(self.randomThree() + y)
      if (self.particles[candidateX][candidateY] == Particle.LAVA):
        self.particles[candidateX][candidateY] = Particle.STONE
        self.particles[x][y] = Particle.NULL
        return
        
    if (random.randrange(1, 6) == 3):
      self.randomTouch(x, y, [Particle.STONE], Particle.SAND)
    self.uptLiquid(x, y, Particle.WATER)

  def uptFire(self, x, y):
    if (random.randrange(1, 6) == 2):
      self.randomTouch(x, y, [Particle.WOOD, Particle.GASOLINE], Particle.FIRE)
    """
    # old code to emit fire into air if flammable material is nearby
    if (self.isTouching(x, y, Particle.WOOD)):
      candidateX = self.clampX(self.randomThree() + x)
      candidateY = self.clampY(self.randomThree() + y)
      if (not self.particlePresent(candidateX, candidateY)):
        self.particles[candidateX][candidateY] = Particle.FIRE
    """
    self.uptGas(x, y, Particle.FIRE)

  def uptAcid(self, x, y):
    for i in range(3):
      self.randomTouch(x, y, [Particle.FIRE], Particle.NULL)
      candidateX = self.clampX(self.randomThree() + x)
      candidateY = self.clampY(self.randomThree() + y)
      if (not (self.particles[candidateX][candidateY] in [Particle.NULL, Particle.WALL, Particle.ACID, Particle.CHAOS, Particle.PLATINUM, Particle.CLONER])):
        self.particles[candidateX][candidateY] = Particle.NULL
        if (random.randrange(1, 2) == 1):
          self.particles[x][y] = Particle.NULL
          return

    self.uptLiquid(x, y, Particle.ACID)

  def uptGasoline(self, x, y):
    # for extra flammability, gasoline actively seeks for heat sources independently
    for i in range(4):
      candidateX = self.clampX(self.randomThree() + x)
      candidateY = self.clampY(self.randomThree() + y)
      if (self.particles[candidateX][candidateY] in [Particle.FIRE, Particle.LAVA, Particle.NAPALM]):
        self.particles[x][y] = Particle.FIRE
        for i in range(3):
          self.randomTouch(x, y, [Particle.GASOLINE, Particle.WOOD, Particle.NULL], Particle.FIRE)
        return

    self.uptLiquid(x, y, Particle.GASOLINE)

  def uptStone(self, x, y):
    self.uptPowder(x, y, Particle.STONE)

  def uptLava(self, x, y):
    self.uptLiquid(x, y, Particle.LAVA)

    self.randomTouch(x, y, [Particle.SAND, Particle.PLATINUM], Particle.LAVA)

    if (random.randint(1, 11) == 3):
      candidateX = self.clampX(self.randomThree() + x)
      candidateY = self.clampY(self.randomThree() + y)
      if (not self.particlePresent(candidateX, candidateY)):
        self.particles[candidateX][candidateY] = Particle.FIRE

    if (random.randint(1, 256) == 3):
      self.particles[x][y] = Particle.STONE

  def uptVirus(self, x, y):
    if self.randomBool():
      self.uptGas(x, y, Particle.VIRUS)
    else:
      self.uptLiquid(x, y, Particle.VIRUS)

    self.randomTouch(x, y, [Particle.VIRUS, Particle.NULL, Particle.WALL, Particle.CHAOS], Particle.VIRUS, True)

  def uptChaos(self, x, y):
    match random.randint(1, 5):
      case 1:
        self.uptPowder(x, y, Particle.CHAOS)
      case 2:
        self.uptLiquid(x, y, Particle.CHAOS)
      case _:
        self.uptGas(x, y, Particle.CHAOS)
    
    self.randomTouch(x, y, [Particle.VIRUS], Particle.CHAOS)

    if (random.randint(1, 200) == 3):
      self.randomTouch(x, y, [Particle.NULL], random.randint(0, 14))
    
    if (random.randint(1, 500) == 2):
      self.particles[x][y] = random.randint(0, 14)

  def uptNapalm(self, x, y):
    if (random.randint(1, 900) == 3):
      self.particles[x][y] = Particle.STONE

    if (random.randint(1, 4) == 2):
      candidateX = self.clampX(self.randomThree() + x)
      candidateY = self.clampY(self.randomThree() + y)
      if (not self.particlePresent(candidateX, candidateY)):
        self.particles[candidateX][candidateY] = Particle.FIRE
    
    self.randomTouch(x, y, [Particle.WATER, Particle.ACID], Particle.STONE)

    self.uptLiquid(x, y, Particle.NAPALM)
    
  def uptVine(self, x, y):
    if (random.randint(1, 5) == 1):
      for i in range(5):
        candidateX = self.clampX(self.randomThree() + x)
        candidateY = self.clampY(self.randomThree() + y)
        if ((not self.particlePresent(candidateX, candidateY)) and self.isTouchingAnythingBut(candidateX, candidateY, [Particle.VINE, Particle.FIRE, Particle.WALL, Particle.NAPALM, Particle.LAVA])):
          self.particles[candidateX][candidateY] = Particle.VINE
    candidateX = self.clampX(self.randomThree() + x)
    candidateY = self.clampY(self.randomThree() + y)
    if (self.clampView(candidateX, candidateY) in [Particle.FIRE, Particle.LAVA]):
        self.clampViewSet(x, y, Particle.FIRE)

  def uptCloner(self, x, y):
    if (random.randint(1, 3) == 1):
      for i in range(8):
        candidateX = self.clampX(self.randomThree() + x)
        candidateY = self.clampY(self.randomThree() + y)
        if (self.particlePresent(candidateX, candidateY) and self.clampView(candidateX, candidateY) != Particle.CLONER and self.clampView(candidateX, candidateY) != Particle.WALL):
          self.surroundSelf(x, y, self.clampView(candidateX, candidateY))
    
  def surroundSelf(self, x, y, pt):
    self.attemptPlace(x + 1, y, pt)
    self.attemptPlace(x - 1, y, pt)
    self.attemptPlace(x, y + 1, pt)
    self.attemptPlace(x, y - 1, pt)
    self.attemptPlace(x + 1, y + 1, pt)
    self.attemptPlace(x - 1, y - 1, pt)
    self.attemptPlace(x + 1, y - 1, pt)
    self.attemptPlace(x - 1, y + 1, pt)
    
  def randomTouch(self, x, y, qt, nt, invertedQueries=False):
    candidateX = self.clampX(self.randomThree() + x)
    candidateY = self.clampY(self.randomThree() + y)
    if ((not (self.particles[candidateX][candidateY] in qt)) if invertedQueries else (self.particles[candidateX][candidateY] in qt)):
      self.particles[candidateX][candidateY] = nt

  def isTouchingAnythingBut(self, x, y, ptlist):
    x = self.clampX(x)
    y = self.clampY(y)

    if  ((not self.clampView(x - 1, y) in ptlist) and self.particlePresent(x - 1, y)):
      return True
    elif ((not self.clampView(x + 1, y) in ptlist) and self.particlePresent(x + 1, y)):
      return True
    elif ((not self.clampView(x + 1, y + 1) in ptlist) and self.particlePresent(x + 1, y + 1)):
      return True
    elif ((not self.clampView(x + 1, y - 1) in ptlist) and self.particlePresent(x + 1, y - 1)):
      return True
    elif ((not self.clampView(x, y + 1) in ptlist) and self.particlePresent(x, y + 1)):
      return True
    elif ((not self.clampView(x, y - 1) in ptlist) and self.particlePresent(x, y - 1)):
      return True
    elif ((not self.clampView(x - 1, y + 1) in ptlist) and self.particlePresent(x - 1, y + 1)):
      return True
    elif ((not self.clampView(x - 1, y - 1) in ptlist) and self.particlePresent(x - 1, y - 1)):
      return True
    else:
      return False

  def isTouching(self, x, y, pt, corners=True):

    x = self.clampX(x)
    y = self.clampY(y)

    if (self.particles[x - 1][y] == pt):
      return True
    elif (self.particles[x + 1][y] == pt):
      return True
    elif (self.particles[x][y + 1] == pt):
      return True
    elif (self.particles[x][y - 1] == pt):
      return True
    
    if corners:
      if (self.particles[x - 1][y + 1] == pt):
        return True
      elif (self.particles[x - 1][y - 1] == pt):
        return True
      elif (self.particles[x + 1][y + 1] == pt):
        return True
      elif (self.particles[x + 1][y - 1] == pt):
        return True
    
    
    return False
  
  def touchingAnything(self, x, y, corners=True):
    x = self.clampX(x)
    y = self.clampY(y)

    if (self.particles[x - 1][y] != Particle.NULL):
      return True
    elif (self.particles[x + 1][y] != Particle.NULL):
      return True
    elif (self.particles[x][y + 1] != Particle.NULL):
      return True
    elif (self.particles[x][y - 1] != Particle.NULL):
      return True
    
    if corners:
      if (self.particles[x - 1][y + 1] != Particle.NULL):
        return True
      elif (self.particles[x - 1][y - 1] != Particle.NULL):
        return True
      elif (self.particles[x + 1][y + 1] != Particle.NULL):
        return True
      elif (self.particles[x + 1][y - 1] != Particle.NULL):
        return True
    
    
    return False

  def uptPowder(self, x, y, pt):
    if not self.particlePresent(x, y + 1):
      self.particles[x][y + 1] = pt
      self.particles[x][y] = Particle.NULL
      return True
    
    corner = self.randomBool()
    cornerX = x

    if (corner == 1):
      cornerX = x + 1
    else:
      cornerX = x - 1

    if not self.particlePresent(cornerX, y + 1):
      self.particles[cornerX][y + 1] = pt
      self.particles[x][y] = Particle.NULL
      return True
    
    return False
  
  def uptLiquid(self, x, y, pt):
    if not self.uptPowder(x, y, pt):
      rightOrLeft = x + 1
      if self.randomBool():
        rightOrLeft = x - 1
      
      if not self.particlePresent(rightOrLeft, y):
        self.particles[rightOrLeft][y] = pt
        self.particles[x][y] = Particle.NULL
        return True
      else:
        rightOrLeft = x - 1
        if self.randomBool():
          rightOrLeft = x + 1
        if not self.particlePresent(rightOrLeft, y):
          self.particles[rightOrLeft][y] = pt
          self.particles[x][y] = Particle.NULL
          return True
        return False
    return True
  
  def uptGas(self, x, y, pt):

    if (random.randrange(1, 50) == 1):
      self.particles[x][y] = Particle.NULL
      return

    candidateX = self.clampX(self.randomThree() + x)
    candidateY = self.clampY(self.randomThree() + y)

    if not self.particlePresent(candidateX, candidateY):
      self.particles[candidateX][candidateY] = pt
      self.particles[x][y] = Particle.NULL
      return True
    
    return False


  def particlePresent(self, x, y):
    if (x > len(self.particles) - 1 or y > len(self.particles[0]) - 1 or x < 0 or y < 0):
      return True
    return self.particles[x][y] != Particle.NULL
  
  def attemptPlace(self, x, y, pt):
    if (not self.particlePresent(x, y)):
      self.particles[x][y] = pt

  

class PGManager:
  def __init__(self, w, h, fps, scale):
    self.width = w
    self.height = h
    self.fps = fps

    #rmx/rmy = raw mouse position not relative to the falling sand simulation
    self.draw = False
    self.mx = 0
    self.my = 0
    self.rmx = 0
    self.rmy = 0
    self.currentParticle = Particle.SAND
    self.mradius = 1

    self.scale = scale

    self.buttons = []
    self.buttons.append((Particle.NULL, "Eraser. Removes particles."))
    self.buttons.append((Particle.SAND, "Sand. Forms small pyramids."))
    self.buttons.append((Particle.WATER, "Water. Gradually fills in spaces."))
    self.buttons.append((Particle.FIRE, "Fire. Ignites flammable materials."))
    self.buttons.append((Particle.WOOD, "Wood. A flammable solid."))
    self.buttons.append((Particle.WALL, "Wall. Indestructable solid."))
    self.buttons.append((Particle.ACID, "Acid. Dissolves most things."))
    self.buttons.append((Particle.GASOLINE, "Gasoline. Highly flammable and explosive."))
    self.buttons.append((Particle.STONE, "Stone. May corrode into sand."))
    self.buttons.append((Particle.LAVA, "Lava. Burns and melts."))
    self.buttons.append((Particle.VIRUS, "Virus. A simulation destroying abomination."))
    self.buttons.append((Particle.CHAOS, "???"))
    self.buttons.append((Particle.PLATINUM, "Platinum. Immune to acid."))
    self.buttons.append((Particle.NAPALM, "Napalm. Fire and lava weren't enough."))
    self.buttons.append((Particle.VINE, "Vine. Grows on things."))
    self.buttons.append((Particle.CLONER, "Cloner. Clones adjacent elements."))

    self.buttonsHover = numpy.full(len(self.buttons), False)
    self.buttonsSelect = numpy.full(len(self.buttons), False)
    self.buttonsSelect[1] = True

    self.paused = False

    self.buttonSize = h / 20
    self.buttonPadding = self.buttonSize * 1.1
    self.buttonHorizontalPadding = self.width / (len(self.buttons) + 1)

    self.notifs = [['Welcome', 120, 0x333333]] # notifcations to render
    self.running = True
    self.connected = False
    self.socket = 0
    self.netupdate = 'nil'
    self.fsg = FSG(int(w / scale), int(h / scale))

    pygame.init()
    self.screen = pygame.display.set_mode((self.width, self.height))
    self.surf = pygame.Surface((w, h))
    self.surf.fill(0xFFFFFF)
    self.font = pygame.font.Font(None, 24)
    self.clock = pygame.time.Clock()

  def __del__(self):
    pygame.quit()

  def drawParticles(self, radius, mx, my, pt):
    endPoint = radius
    endPointY = radius
    if (mx + radius > self.width / self.scale):
      endPoint -= (int(mx + radius) - int(self.fsg.clampX(mx + radius)))
    if (my + radius > self.height / self.scale):
      endPointY -= (int(my + radius) - int(self.fsg.clampY(my + radius)))
    for x in range(-radius, endPoint):
      for y in range(-radius, endPointY):
        self.fsg.particles[int(round(mx + x))][int(round(my + y))] = pt

  def handleEvents(self):
    for e in pygame.event.get():
      if e.type == pygame.QUIT:
        self.running = False
      elif e.type == pygame.MOUSEBUTTONDOWN:
        self.draw = True
      elif e.type == pygame.MOUSEBUTTONUP:
        self.draw = False
      elif e.type == pygame.MOUSEMOTION:
        self.rmx, self.rmy = pygame.mouse.get_pos()
        self.mx, self.my = pygame.mouse.get_pos()
        self.mx /= self.scale
        self.my /= self.scale
        self.mx = round(max(0, min(self.mx, self.fsg.width - 1)))
        self.my = round(max(0, min(self.my, self.fsg.height - 1)))
      elif e.type == pygame.MOUSEWHEEL:
        if (e.y > 0):
          self.mradius += 1
        elif (e.y < 0):
          self.mradius -= 1
      elif e.type == pygame.KEYDOWN:
        if e.key == pygame.K_SPACE:
          self.paused = not self.paused
          if self.connected:
            self.netupdate = struct.pack('<?bhhb', self.paused, 0, self.mx, self.my, self.currentParticle)
        elif e.key == pygame.K_c:
          if self.connected:
            self.disconnectFromServer()
          else:
            self.connectToServer()
    
    if self.mradius < 1:
      self.mradius = 1
    
    if self.draw:
      if self.rmy > self.buttonPadding * 2:
        self.drawParticles(self.mradius, self.mx, self.my, self.currentParticle)
        if self.connected:
          self.netupdate = struct.pack('<?bhhb', self.paused, self.mradius, self.mx, self.my, self.currentParticle)

    for i, bt in enumerate(self.buttons):
      if ((self.rmx > ((i + 1) * self.buttonHorizontalPadding) - (self.buttonSize / 2) and self.rmx < ((i + 1) * self.buttonHorizontalPadding) + (self.buttonSize / 2)) and self.rmy < self.buttonPadding * 2):
        self.buttonsHover[i] = True
        if self.draw:
          if self.currentParticle != self.buttons[i][0]:
            self.notifs.append(['{} selected'.format(self.buttons[i][1].split(' ')[0][:-1]), 60, (51, 51, 51)])
          self.currentParticle = self.buttons[i][0]
          self.buttonsSelect = numpy.full(len(self.buttons), False)
          self.buttonsSelect[i] = True
      else:
        self.buttonsHover[i] = False
        

  def pauseDeltaTime(self):
    self.clock.tick(self.fps)

  def connectToServer(self):
    self.connected = True
    self.socket = socket.socket()
    self.socket.settimeout(1.5)
    try:
      self.socket.connect((IP, PORT))
      self.socket.setblocking(False)
      self.notifs.append(["Connection success", 120, (48, 192, 48)])
    except TimeoutError as te:
      self.connected = False
      self.notifs.append(["Server failed to respond. (May not be running)", 300, (192, 48, 48)])
    except Exception as e:
      self.connected = False
      self.notifs.append(["Connection failure: {}".format(repr(e)), 300, (192, 48, 48)])
    
    #cprint(self.socket.recv(1024)) # print connection message

  def disconnectFromServer(self):
    self.connected = False
    self.socket.close()
    self.notifs.append(["Disconnected", 120, (192, 128, 48)])
    self.socket = 0

  def update(self):
    global grad
    grad += 7
    if (not self.paused):
     self.fsg.update()
    for n in self.notifs:
      n[1] = n[1] - 1

    self.notifs = list(filter(lambda n: n[1] >= 0, self.notifs))

  def render(self):
    pygame.draw.rect(self.screen, 0xFFFFFF, (0, 0, self.width, self.height))
    global grad
    global simgrad

    simgrad = grad
    temp = grad

    x = 0
    for col in self.fsg.particles:
      y = 0
      for p in col:
        simgrad += 1
        simgrad %= 1536
        if p != Particle.NULL:
          grad = simgrad
          clr = getColor(self.fsg.particles[x][y])
          pygame.draw.rect(self.screen, clr, (x * self.scale, y * self.scale, self.scale, self.scale))
          
        y += 1
      x += 1

    grad = temp

    # render ui buttons & text
    pygame.draw.rect(self.screen, 0xFFFFFF, (0, 0, self.width, self.buttonPadding * 2))

    textRenderer = self.font.render('Try an above element. Scroll to change drawing size. Space to pause.', False, 0x333333)

    for i, button in enumerate(self.buttons):
      outline = 0x444444

      if (self.buttonsHover[i]):
        outline = 0xAAAAAA
        textRenderer = self.font.render(button[1], False, 0x333333)

      pygame.draw.rect(self.screen, outline, (int(((i + 1) * (self.buttonHorizontalPadding)) - (self.buttonSize / 2)) - 1, int(self.buttonPadding / 2) - 1, int(self.buttonSize) + 2, int(self.buttonSize) + 2))
      pygame.draw.rect(self.screen, getColor(button[0]), (int(((i + 1) * (self.buttonHorizontalPadding)) - (self.buttonSize / 2)), int(self.buttonPadding / 2), int(self.buttonSize), int(self.buttonSize)))

      if (self.buttonsSelect[i]):
        pygame.draw.circle(self.screen, outline, (int(((i + 1) * (self.buttonHorizontalPadding)) - (self.buttonSize / 2)) + (self.buttonSize / 2), int(self.buttonPadding / 2) + (self.buttonSize / 2)), self.buttonSize / 4)
      

    pygame.draw.line(self.screen, 0xDDDDDD, (0, self.buttonPadding * 2), (self.width, self.buttonPadding * 2), 1)

    self.screen.blit(textRenderer, (5, self.buttonPadding * 2.1, 100, self.buttonPadding))

    if (self.paused):
      textRenderer = self.font.render("PAUSED", False, (51, 51, 51))
      self.screen.blit(textRenderer, (5, self.buttonPadding * 3.1, 100, self.buttonPadding))

    # render notifications & measure distance from edge
    i = 1
    for n in reversed(self.notifs):
      textRenderer = self.font.render(n[0], False, n[2])
      leng = functools.reduce(lambda acc, cur: cur[4] + acc, self.font.metrics(n[0]), 0)
      self.screen.blit(textRenderer, (WINDOW_WIDTH - (9 + leng), (WINDOW_HEIGHT - (self.buttonPadding * i)), 100, self.buttonPadding))
      i += 1

    if self.connected:
      textRenderer = self.font.render('C', False, (16, 240, 240))
      self.screen.blit(textRenderer, (5, (WINDOW_HEIGHT - 20), 100, self.buttonPadding))
    
    pygame.display.update()



WINDOW_WIDTH = 600
WINDOW_HEIGHT = 480
SCALE = 4
# address of server
IP = '192.168.1.12'
PORT = 40999 

"""
  data takes following form:
  1 byte = pause state
  1 byte = radius (can be zero- no placement)
  2 bytes = mouse X
  2 bytes = mouse Y
  1 byte = element type

  '<?bhhb'
"""

def checkUpdates(game):
  try:
    data = struct.unpack('<?bhhb', game.socket.recv(1024))
    paused = (data[0] == 1)
    rad = data[1]
    mouseX = data[2]
    mouseY = data[3]
    type = data[4]

    random.seed(5)
    game.drawParticles(rad, mouseX, mouseY, type)
    game.paused = paused
  except:
    return

def sendUpdates(game):
  if game.netupdate != 'nil':
    try:
      game.socket.send(game.netupdate)
    except:
      game.connected = False
      game.notifs.append(["Server connection ended", 120, (192, 48, 48)])
    game.netupdate = 'nil'

def main():
  game = PGManager(WINDOW_WIDTH, WINDOW_HEIGHT, 24, SCALE)
  #skt = socket.socket()
  #skt.bind(())


  while (game.running):
    game.handleEvents()

    game.update()

    game.render()

    game.pauseDeltaTime()

    if game.connected:
      sendUpdates(game)
      checkUpdates(game)

if __name__ == "__main__":
  main()

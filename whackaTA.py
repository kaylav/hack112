from pykinect2 import PyKinectV2, PyKinectRuntime
from pykinect2.PyKinectV2 import *

import ctypes
import _ctypes
import pygame
import sys
import math
import random
import copy
from PIL import Image
from pygame.locals import *

class targets(object):
    def __init__(self):

        pygame.init()
        pygame.font.init

        self.intro = True
        self.timer = 0
        self.screen_width = 960
        self.screen_height = 540
        #self.prev_right_hand_height = 0
        #self.prev_left_hand_height = 0
        self.cur_right_hand_x = 0
        self.cur_right_hand_y = 0
        self.cur_left_hand_x = 0
        self.cur_left_hand_y = 0

        # Used to manage how fast the screen updates
        self.clock = pygame.time.Clock()

        # Set the width and height of the window [width/2, height/2]
        self.screen = pygame.display.set_mode((self.screen_width,self.screen_height), pygame.HWSURFACE|pygame.DOUBLEBUF, 32)

        # Loop until the user clicks the close button.
        self.done = False

        self.state = "start"
        # Kinect runtime object, we want color and body frames
        self.kinect = PyKinectRuntime.PyKinectRuntime(PyKinectV2.FrameSourceTypes_Color | PyKinectV2.FrameSourceTypes_Body)

        # back buffer surface for Kinect color frames, 32bit color, width and height equal to the Kinect color frame size
        self.frame_surface = pygame.Surface((self.kinect.color_frame_desc.Width, self.kinect.color_frame_desc.Height), 0, 32)

        # here we will store skeleton data
        self.bodies = None

        # initialize the target data
        self.circleList = [] #[(self.screen_width//2, self.screen_height//2), 100]
        self.activatedList = []

        self.circleFinalR = 150 # final radius for every circle 
        self.circleX = random.randint(self.screen_width//4, self.screen_width*3//4)
        self.circleY = random.randint(0, self.screen_height*3//4) #, self.screen_height)

        self.score = 0
        pygame.font.init()
        gameFont = pygame.font.SysFont('Arial', 30)
        self.TAlist = ['images/chris.png','images/doug.png', 'images/hadley.png', \
        'images/kyle.png','images/subra.png']
        self.activatedTAIndicies= []

    def generate(self):
        if self.timer % 500 == 0 and (len(self.activatedList) + len(self.circleList)) < 5:
            radius = 10 # magic number
            x = random.randint(radius,self.screen_width-radius)
            y = random.randint(radius,self.screen_height-radius)
            target = ((x,y),radius)
            self.circleList.append(target)



    def drawCircles(self):
        #print("in draw circles")
        for item in self.circleList:
            color = (200,0,0)
            coord = item[0]
            radius = item[1]
            pygame.draw.circle(self.frame_surface, color, coord, radius)


    def drawActivated(self):
        #print("In activated")
        #while len(self.activatedList) > 0:
        for item in self.activatedList:
            color = (0,0,200)
            coordx = item[0][0]
            coordy = item[0][1]
            radius = item[1]

            index = self.activatedList.index(item)


            img = pygame.transform.scale(pygame.image.load(self.TAlist[index]).convert_alpha(),(300, 300))
            #self.screen = pygame.display.set_mode(coord)
            self.frame_surface.blit(img, ((coordx-radius), (coordy - radius)))
            #TODO: #draw image at specific coords with radius
            #img = Image.open("arman.png")
            #pygame.draw.circle(self.frame_surface, color, coord, radius)
            #img = pygame.image.load('arman.png')
            #TAfaces(img, coord)

    def checkTarget(self):
        temp = []

        for item in self.circleList:
            radius = item[1]
            if radius >= self.circleFinalR:
                self.activatedList.append(item)
                i = random.randint(0, len(self.TAlist)-1)
                self.activatedTAIndicies.append(i)
            else:
                temp.append(item)
        self.circleList = temp
        #print("circleList length: ", len(self.circleList))
        # print("activatedList length: ", len(self.activatedList))
        if len(self.activatedList) >= 5:
            self.state = "over"

    def growTarget(self):
        #print("in growTarget")
        self.checkTarget()
        for i in range(len(self.circleList)):
            x,y = self.circleList[i][0]
            radius = self.circleList[i][1]
            self.circleList[i] = ((x,y),radius+5)

    def checkStart(self):
        circle = (self.screen_width // 2, self.screen_height // 2)
        #if self.cur_right_hand_x == circle[0] and self.cur_right_hand_y == circle[1]:

        diff = ((circle[0] - self.cur_right_hand_x)**2 + (circle[1] - self.cur_right_hand_y)**2)**(0.5)
        if diff < 30:
            self.state = "game"

    def drawStart(self):
        # print("In drawStart")
        # you have to call this at the start,
                   # if you want to use this module.

        # If all goes to shit, undo these:
        myfont = pygame.font.SysFont('Comic Sans MS', 100)
        textsurface = myfont.render('Wack-a-Staff', True, (55,0,0)) #msg, true, color
        self.screen.blit(textsurface,(145,100))





    def drawOver(self):
        myfont = pygame.font.SysFont('Comic Sans MS', 80)
        textsurface = myfont.render('To restart: press r', True, (55,0,0)) #msg, true, color
        self.screen.blit(textsurface,(50,100))

    def drawGame(self):
        myfont = pygame.font.SysFont('Comic Sans MS', 30)
        text = "Score: %d" % (self.score)
        textsurface = myfont.render(text, True, (55,0,0)) #msg, true, color
        self.screen.blit(textsurface,(20,20))


    def draw_color_frame(self, frame, target_surface):
        target_surface.lock()
        address = self.kinect.surface_as_array(target_surface.get_buffer())
        ctypes.memmove(address, frame.ctypes.data, frame.size)
        del address
        target_surface.unlock()

    def run(self):
        # -------- Main Program Loop -----------


        while not self.done:
            if self.timer % 20 == 0 and self.state == 'game':
                self.generate()
                self.growTarget()



            # --- Main event loop
            for event in pygame.event.get(): # User did something
                if event.type == pygame.QUIT: # If user clicked close
                    self.done = True # Flag that we are done so we exit this loop
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_c and self.state == "start":
                        self.state = "game"
                    elif event.key == pygame.K_r and self.state == "over":
                        print("heyo")
                        self.state = "game"
                        self.circleList = []
                        self.activatedList = []
                        self.sdcore = 0

            # We have a color frame. Fill out back buffer surface with frame's data
            if self.kinect.has_new_color_frame():
                frame = self.kinect.get_last_color_frame()
                self.draw_color_frame(frame, self.frame_surface)
                frame = None

            # We have a body frame, so can get skeletons
            if self.kinect.has_new_body_frame():
                self.bodies = self.kinect.get_last_body_frame()

                if self.bodies != None:
                    for i in range(0, self.kinect.max_body_count):
                        body = self.bodies.bodies[i]
                        if not body.is_tracked:
                            continue

                        joints = body.joints
                        # convert joint coordinates to color space


                        if joints[PyKinectV2.JointType_HandRight].TrackingState != PyKinectV2.TrackingState_NotTracked:
                            self.cur_right_hand_x = abs((joints[PyKinectV2.JointType_HandTipRight].Position.x + 1.5)/3 * 1920)
                            self.cur_right_hand_y = abs((joints[PyKinectV2.JointType_HandTipRight].Position.y - 0.5) * 1080)
                            # print("updating")
                        if joints[PyKinectV2.JointType_HandLeft].TrackingState != PyKinectV2.TrackingState_NotTracked:
                            self.cur_left_hand_x = abs((joints[PyKinectV2.JointType_HandTipLeft].Position.x + 1.5)/3 * 1920)
                            self.cur_left_hand_y = abs((joints[PyKinectV2.JointType_HandTipLeft].Position.y - 0.5) * 1080)

                        if self.state == "start":
                            self.drawStart()

                            # check to see if the hand is in the starting positions, then start the game
                            # call draw start (includes instructions, starting circle)
                            pass
                        elif self.state == "over":
                            # call draw end screen (end score, how to restart game)
                            pass
                        else:
                        # call check target to get the full list
                            self.checkTarget()
                            # calculate distance between center of circle and hand
                            # need to calculate distance between EVERY circle and hand


                            tempList = copy.deepcopy(self.activatedList)
                            if len(self.activatedList) <= 5:
                                for item in self.activatedList:
                                    #print("cx", item[0][0])
                                    #print("cy", item[0][1])
                                    rightDist = math.sqrt((self.cur_right_hand_x-item[0][0])**2+(self.cur_right_hand_y-item[0][1])**2)
                                   # leftDist = math.sqrt((self.cur_left_hand_x-item[0][0])**2+(self.cur_left_hand_y-item[0][1])**2)
                                    if (rightDist < 150): #or (leftDist < 20)):
                                        tempList.remove(item)
                                        self.score += 1
                                self.activatedList = tempList




            self.drawCircles()
            self.drawActivated()

            # --- Game logic
            self.timer += 5


            # Optional debugging text
            #font = pygame.font.Font(None, 36)
            #text = font.render(str(self.flap), 1, (0, 0, 0))
            #self.frame_surface.blit(text, (100,100))

            # --- copy back buffer surface pixels to the screen, resize it if needed and keep aspect ratio
            # --- (screen size may be different from Kinect's color frame size)
            h_to_w = float(self.frame_surface.get_height()) / self.frame_surface.get_width()
            target_height = int(h_to_w * self.screen.get_width())
            surface_to_draw = pygame.transform.scale(self.frame_surface, (self.screen.get_width(), target_height));
            self.screen.blit(surface_to_draw, (0,0))
            surface_to_draw = None

            if self.state == "start":
                self.drawStart()
            if self.state == "game":
                self.drawGame()
            if self.state == "over":
                self.drawOver()

            pygame.display.update()
            pygame.display.flip()


            # --- Limit to 60 frames per second
            self.clock.tick(60)


        # Close our Kinect sensor, close the window and quit.
        self.kinect.close()
        pygame.quit()

    #TAs = ["arman.png",]
    #randTA = random.randint(0, len(TAs)-1)
    #TA = TAs[]
    #img = Image.open("arman.png")
    #python imaging library

game = targets();
game.run();

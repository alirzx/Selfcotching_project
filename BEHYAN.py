import streamlit as st
import cv2
import mediapipe as mp
import numpy as np
import pygame
#from utils import calculate_angle , get_landmark_array, get_landmark_features, rounded_rectangle, draw_pose, nothing


def calculate_angle (a,b,c) :
    a = np.array(a) #first
    b = np.array(b) # Mid
    c = np.array(c) # End

    radians = np.arctan2(c[1]-b[1], c[0]-b[0])  - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians*180.0/np.pi)

    if angle > 180.0 :
        angle= 360 - angle

    return int(angle)


def get_landmark_array(pose_landmark, key):

    denorm_x = pose_landmark[key].x
    denorm_y = pose_landmark[key].y

    return np.array([denorm_x, denorm_y])




def get_landmark_features(kp_results, dict_features, feature):

    if feature == 'nose':
        return get_landmark_array(kp_results, dict_features[feature])

    elif feature == 'left' or 'right':
        shldr_coord = get_landmark_array(kp_results, dict_features[feature]['shoulder'])
        elbow_coord   = get_landmark_array(kp_results, dict_features[feature]['elbow'])
        wrist_coord   = get_landmark_array(kp_results, dict_features[feature]['wrist'])
        thumb_coord   = get_landmark_array(kp_results, dict_features[feature]['thumb'])
        hip_coord   = get_landmark_array(kp_results, dict_features[feature]['hip'])
        foot_coord   = get_landmark_array(kp_results, dict_features[feature]['foot'])

        return shldr_coord, elbow_coord, wrist_coord,thumb_coord,hip_coord,foot_coord
    

def rounded_rectangle(img,a,b,c,d,radius,color):

    # Define the position and size of the rectangle
    x, y, width, height = a, b, c, d


    # Draw the rounded rectangle on the image
    cv2.ellipse(img, (x + radius, y + radius), (radius, radius), 180, 0, 90, color, -1)
    cv2.ellipse(img, (x + width - radius, y + radius), (radius, radius), 270, 0, 90, color, -1)
    cv2.ellipse(img, (x + width - radius, y + height - radius), (radius, radius), 0, 0, 90, color, -1)
    cv2.ellipse(img, (x + radius, y + height - radius), (radius, radius), 90, 0, 90, color, -1)
    cv2.rectangle(img, (x + radius, y), (x + width - radius, y + height), color, -1)
    cv2.rectangle(img, (x, y + radius), (x + width, y + height - radius), color, -1)


# def play_sound(feedback,speech) :
#     counters['feedback_distance_counter'] = 0 
#     speech.play()
#     stage_and_state['feedback'] = feedback

    
    
def draw_pose (image ,results ,color,mp_drawing,mp_pose):
    #render detections
    #DRAW POSE LANDMARKS ON IMAGE
    mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                              mp_drawing.DrawingSpec(color= color, thickness=2 ,circle_radius=1),
                              mp_drawing.DrawingSpec(color= color, thickness=2,circle_radius=1)
                              )

    
# def feedback_show(image, feedback ,speech) :
#     rounded_rectangle(image,90,275,240,45,20,COLORS['dark_orange'])
#     cv2.putText(image,feedback,(100,300),
#         cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,0,0),1,cv2.LINE_AA)
#     #if s2 == 0 :
#     counters['feedback_distance_counter'] += 1s
     
#     if stage_and_state['feedback'] != feedback :
#             if counters['feedback_distance_counter'] > another_treshs['feedback_distance_tresh'] :
        
#                 speech.play()
#                 stage_and_state['feedback'] = feedback
#                 counters['feedback_distance_counter'] = 0
    
    
    
def nothing(x):
    pass



def main_procces () :
    Easy_Body_treshs = {
        'l_elbow_correct_range' : (135,180),
        'r_elbow_correct_range' : (135,180),
        'l_wrist_correct_range' : (110, 175),
        'r_wrist_correct_range' : (110, 175),
        'shoulder_correct_range' : (10,110)
        }
#     Hard_Body_treshs = {
#         'l_elbow_correct_range' : (150,177),
#         'r_elbow_correct_range' : (150,177),
#         'l_wrist_correct_range' : (120, 175),
#         'r_wrist_correct_range' : (120, 175),
#         'shoulder_correct_range' : (15,105)
#         }

    another_treshs = {
        'down_tresh' : 25,
        'up_tresh' : 75,
        'inactive_tresh' : 90,
        'front_tresh' : 40,
        'speed_tresh' : (8,25),
        'feedback_distance_tresh' : 50,
        'num_correct_tresh' : 10
        }


    counters = {
        'correct' : 0,
        'incorrect' : 0,
        'down_stage_counter' : 0,
        'first_speed_counter' : 0,
        'second_speed_counter' : 0,
        'state_counter' : 0,
        'feedback_distance_counter' : 0,
        'num_correct_counter' : 0
        }

    stage_and_state = {

        'front_stage' : None,
        'stage' : None,
        'feedback' : None,
        'False_state_sequence' :[]

        }

    COLORS = {
                'blue'       : (0, 127, 255),
                'red'        : (50, 50, 255),
                'green'      : (10, 255, 0),
                'light_green': (100, 233, 127),
                'yellow'     : (255, 255, 0),
                'magenta'    : (255, 0, 255),
                'white'      : (255,255,255),
                'cyan'       : (0, 255, 255),
                'light_blue' : (102, 204, 255),
                'dark_turquoise' : (209,206,0),
                 'black'         : (0,0,0),
                'dark_orange'  : (0,140,255),
                'white_bone'  :   (220,220,220),
                'orange_red' : (0,69,255)
                      }




    # Dictionary to maintain the various landmark features.
    dict_features = {}
    Angles = {}
    
    left_features = {
                        'shoulder': 11,
                        'elbow'   : 13,
                        'wrist'   : 15,
                        'thumb'   : 21,
                        'hip'     : 23,
                        'foot'    : 31
                            }

    right_features = {
                        'shoulder': 12,
                        'elbow'   : 14,
                        'wrist'   : 16,
                        'thumb'   : 22,
                        'hip'     : 24,
                        'foot'    : 32
                            }

    dict_features['left'] = left_features
    dict_features['right'] = right_features
    dict_features['nose'] = 0





    mp_drawing = mp.solutions.drawing_utils
    mp_pose = mp.solutions.pose

    # Load the audio files
    pygame.mixer.init()
    cap = cv2.VideoCapture(0)

    # frame_width = 840
    # frame_height = 680

    # # Set the display window size
    # cv2.namedWindow('BEHYAN', cv2.WINDOW_NORMAL)
    # cv2.resizeWindow('BEHYAN', frame_width, frame_height)

    # # create switch for Easy/Hard functionality for taskbar
    # switch1 = ' EASY \ HARD'
    # cv2.createTrackbar(switch1, 'BEHYAN',0,1,nothing)

    # switch2 = 'sound'
    # cv2.createTrackbar(switch2, 'BEHYAN',0,1,nothing)


    shoulders_mp3 = pygame.mixer.Sound('files/close_shoulders.mp3')
    left_shoulder_mp3  = pygame.mixer.Sound('files/close_left shoulder.mp3')
    right_shoulder_mp3  = pygame.mixer.Sound('files/close_right_shoulder.mp3')
    close_elbows_mp3 = pygame.mixer.Sound('files/close_the_elbows.mp3')
    close_left_elbow_mp3 = pygame.mixer.Sound('files/close_left_elbow.mp3')
    close_right_elbow_mp3 = pygame.mixer.Sound('files/close_right_elbow.mp3')
    open_elbows_mp3 = pygame.mixer.Sound('files/open_the_elbows.mp3')
    open_left_elbow_mp3 = pygame.mixer.Sound('files/open_left_elbow.mp3')
    open_right_elbow_mp3 = pygame.mixer.Sound('files/open_right_elbow.mp3')
    be_front_mp3 = pygame.mixer.Sound('files/be_front.mp3')
    #inanctive_time_mp3 = pygame.mixer.Sound('files/INACTIVE_TIME.mp3')
    # faster_mp3 = pygame.mixer.Sound('should_be_faster.mp3')
    # slower_mp3 = pygame.mixer.Sound('should_be_slower.mp3')



    # SETUP MEDIAPIPE INSTANCE
    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5,static_image_mode = False,model_complexity = 1,smooth_landmarks = True) as pose:
        while cap.isOpened():
            ret, frame = cap.read()
            if ret == False :
                print('camera can not open!')

            #recolor image to RGB
            # CONVERT FRAME TO RGB FOR MEDIAPIPE
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False

            #make detections

            # PROCESS IMAGE WITH MEDIAPIPE POSE ESTIMATION
            results = pose.process(image)

            #recolor back to BGR
            # CONVERT IMAGE BACK TO BGR FOR OPENCV DISPLAY
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)


            #Extract Landmarks

            try :
                landmarks = results.pose_landmarks


                #All the keypoints we need to use for caculate Angles
                #get cordinates
                nose = get_landmark_features(landmarks.landmark,dict_features, 'nose')
                left_shoulder, left_elbow, left_wrist,left_thumb,left_hip,left_foot = \
                                    get_landmark_features(landmarks.landmark,dict_features, 'left')
                right_shoulder, right_elbow, right_wrist,right_thumb,right_hip,right_foot = \
                                    get_landmark_features(landmarks.landmark,dict_features, 'right')


      ###################################################################################################
                #calculate nose angle
                front_angle = calculate_angle(right_shoulder,nose,left_shoulder)
    #            print(f'front_angle{front_angle}')

                if front_angle > another_treshs['front_tresh'] :
    ############
                    stage_and_state['front_stage'] = 'FRONT'

    #                print(f'front_stage : {front_stage}')


    #                dist_l_sh_hip = abs(left_foot[1]- left_shoulder[1])
    #                dist_r_sh_hip = abs(right_foot[1] - right_shoulder[1])
    #                print(dist_l_sh_hip)
    #                print(dist_r_sh_hip)

            
   #######################################################################################         
                       #for progress bar
                    cv2.rectangle(image,(198,20),(634,26),COLORS['black'],1)
                    
                    cv2.putText(image,'Reps',(198,13),
                                cv2.FONT_HERSHEY_TRIPLEX,0.3,COLORS['black'],1,cv2.LINE_AA)
#                     cv2.putText(image,str(counters['num_correct_counter']),(207,17),
#                                 cv2.FONT_HERSHEY_TRIPLEX,0.5,COLORS['black'],1,cv2.LINE_AA)
#                     cv2.putText(image,str(another_tershs['num_correct_tresh']),(213,17),
#                                 cv2.FONT_HERSHEY_TRIPLEX,0.5,COLORS['black'],1,cv2.LINE_AA)
                    
                    #numbers of correct exercise should be done for finish exercise (for progress bar)
                    number_correct = 436 // another_treshs['num_correct_tresh']
                    #start and end of first part of progress bar
                    p1,p2,p3,p4 = 201,23,244,23
 ###########################################################################################                   
                     #setup states box
                    rounded_rectangle(image,10,10,185,80,25,COLORS['black'])
        
                    # Rep corecct Data
                    cv2.putText(image,'correct',(17,27),
                                cv2.FONT_HERSHEY_TRIPLEX,0.5,(0,255,0),1,cv2.LINE_AA)
                    cv2.putText(image,str(counters['correct']),
                                (30,70),
                                cv2.FONT_HERSHEY_TRIPLEX,1,(0,255,0),1,cv2.LINE_AA)

                    # Rep incorecct Data
                    cv2.putText(image,'incorrect',(93,27),
                                cv2.FONT_HERSHEY_TRIPLEX,0.5,(0,0,255),1,cv2.LINE_AA)
                    cv2.putText(image,str(counters['incorrect']),
                                (110,70),
                                cv2.FONT_HERSHEY_TRIPLEX,1,(0,0,255),1,cv2.LINE_AA)

                    # stage Data
    #                 cv2.putText(image,'Stage',(195,12),
    #                             cv2.FONT_HERSHEY_TRIPLEX,0.5,(255,0,0),1,cv2.LINE_AA)
    #                 cv2.putText(image,str(stage_and_state['stage']),
    #                             (170,60),
    #                             cv2.FONT_HERSHEY_TRIPLEX,1,(255,0,0),1,cv2.LINE_AA)

    #                 # left and right side 
    #                 cv2.putText(image,'Left :',(315,40),
    #                             cv2.FONT_HERSHEY_TRIPLEX,0.5,(255,0,255),1,cv2.LINE_AA)

    #                 cv2.putText(image,'Right :',(315,60),
    #                             cv2.FONT_HERSHEY_TRIPLEX,0.5,(255,0,255),1,cv2.LINE_AA)




    #                if dist_l_sh_hip > dist_r_sh_hip :
    #                        front_side = 'LEFT'
    #                        print(f'front_side : {front_side}')
                    
        
                    
                    
                    #calculate left angles 

                    #elbow
                    left_elbow_angle = calculate_angle(left_shoulder,left_elbow,left_wrist)


                    #wrist
                    left_wrist_angle = calculate_angle(left_elbow,left_wrist,left_thumb)


                    #shoulder
                    left_shoulder_angle = calculate_angle(left_elbow,left_shoulder,left_hip)

    #               print(f'left angle elbow : {left_elbow_angle}')
    #               print(f'left angle wrist : {left_wrist_angle}')
    #               print(f'left angle shoulder : {left_shoulder_angle}')

                     #calculate right angle

                     #elbow
                    right_elbow_angle = calculate_angle(right_shoulder,right_elbow,right_wrist)


                    #wrist
                    right_wrist_angle = calculate_angle(right_elbow,right_wrist,right_thumb)


                    #shoulder
                    right_shoulder_angle = calculate_angle(right_elbow,right_shoulder,right_hip)

                    Angles['left_elbow_angle'] =  left_elbow_angle
                    Angles['left_wrist_angle'] =  left_wrist_angle
                    Angles['left_shoulder_angle'] =  left_shoulder_angle
                    Angles['right_elbow_angle'] =  right_elbow_angle
                    Angles['right_wrist_angle'] =  right_wrist_angle
                    Angles['right_shoulder_angle'] =  right_shoulder_angle
####################
    #                print(f'ANGLES: {Angles}')
    #                print(f'right angle wrist : {Angles["right_wrist_angle"]}')
    #                print(f'right angle shoulder : {Angles["right_shoulder_angle"]}')


     ###############################################################################################################                       


    #                 #visualize angles on the body

    #                 #visualize left elbow angle
    #                 cv2.putText(image,str(Angles['left_elbow_angle']),
    #                     tuple(np.multiply(left_elbow, [640,480]).astype(int)),
    #                     cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0),2,cv2.LINE_AA
    #                         )
    #                 #visualize left wrist angle
    #                 cv2.putText(image,str(Angles['left_wrist_angle']),
    #                     tuple(np.multiply(left_wrist,[640,480]).astype(int)),
    #                     cv2.FONT_HERSHEY_SIMPLEX, 0.5,(0,0,0),2,cv2.LINE_AA
    #                         )
    #                 #visualize Left shoulder angle
    #                 cv2.putText(image,str(Angles['left_shoulder_angle']),
    #                     tuple(np.multiply(left_shoulder,[640,480]).astype(int)),
    #                     cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,0,0),2,cv2.LINE_AA
    #                         )


    #                 #visualize right elbow angle
    #                 cv2.putText(image,str(Angles['right_elbow_angle']),
    #                     tuple(np.multiply(right_elbow, [640,480]).astype(int)),
    #                     cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0),2,cv2.LINE_AA
    #                         )
    #                 #visualize right wrist angle
    #                 cv2.putText(image,str(Angles['right_wrist_angle']),
    #                     tuple(np.multiply(right_wrist,[640,480]).astype(int)),
    #                     cv2.FONT_HERSHEY_SIMPLEX, 0.5,(0,0,0),2,cv2.LINE_AA
    #                         )
    #                 #visualize right shoulder angle
    #                 cv2.putText(image,str(Angles['right_shoulder_angle']),
    #                     tuple(np.multiply(right_shoulder,[640,480]).astype(int)),
    #                     cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,0,0),2,cv2.LINE_AA
    #                         )



    ###############################################################################################


    #                 s1 = cv2.getTrackbarPos(switch1,'BEHYAN')
    #                 #print(f'switch easy hard :{s1}')

    #                 s2 = cv2.getTrackbarPos(switch2,'BEHYAN')
    #                 #print(f'switch sound : {s2}')

                     #if s1 == 0:
####################
                    is_left_elbow_correct  = Easy_Body_treshs['l_elbow_correct_range'][0] <= Angles['left_elbow_angle'] <= Easy_Body_treshs['l_elbow_correct_range'][1]
                    is_left_wrist_correct = Easy_Body_treshs['l_wrist_correct_range'][0] <= Angles['left_wrist_angle'] <= Easy_Body_treshs['l_wrist_correct_range'][1]
                    is_left_shoulder_correct = Easy_Body_treshs['shoulder_correct_range'][0] <= Angles['left_shoulder_angle'] <= Easy_Body_treshs['shoulder_correct_range'][1]

                    is_right_elbow_correct  = Easy_Body_treshs['r_elbow_correct_range'][0] <= Angles['right_elbow_angle'] <= Easy_Body_treshs['r_elbow_correct_range'][1]
                    is_right_wrist_correct = Easy_Body_treshs['r_wrist_correct_range'][0] <= Angles['right_wrist_angle'] <= Easy_Body_treshs['r_wrist_correct_range'][1]
                    is_right_shoulder_correct = Easy_Body_treshs['shoulder_correct_range'][0] <= Angles['right_shoulder_angle'] <= Easy_Body_treshs['shoulder_correct_range'][1]
                    
                    
                    
 ####################################################################
                    
#############################################################################################################
                
    #                 else :

    #                     is_left_elbow_correct  = Hard_Body_treshs['l_elbow_correct_range'][0] <= Angles['left_elbow_angle'] <= Hard_Body_treshs['l_elbow_correct_range'][1]
    #                     is_left_wrist_correct = Hard_Body_treshs['l_wrist_correct_range'][0] <= Angles['left_wrist_angle'] <= Hard_Body_treshs['l_wrist_correct_range'][1]
    #                     is_left_shoulder_correct = Hard_Body_treshs['shoulder_correct_range'][0] <= Angles['left_shoulder_angle'] <= Hard_Body_treshs['shoulder_correct_range'][1]

    #                     is_right_elbow_correct  = Hard_Body_treshs['r_elbow_correct_range'][0] <= Angles['right_elbow_angle'] <= Hard_Body_treshs['r_elbow_correct_range'][1]
    #                     is_right_wrist_correct = Hard_Body_treshs['r_wrist_correct_range'][0] <= Angles['right_wrist_angle'] <= Hard_Body_treshs['r_wrist_correct_range'][1]
    #                     is_right_shoulder_correct = Hard_Body_treshs['shoulder_correct_range'][0] <= Angles['right_shoulder_angle'] <= Hard_Body_treshs['shoulder_correct_range'][1]




                    #if is_left_elbow_correct and is_left_shoulder_correct and is_right_elbow_correct and is_right_shoulder_correct :
                        
                        
    ###########################################################################################################

                     #visualize left side angles on rectangle

                    # shoulder Data
    #                 cv2.putText(image,'shoulder',(360,12),
    #                         cv2.FONT_HERSHEY_TRIPLEX,0.5,(205,116,24),1,cv2.LINE_AA)
    #                 cv2.putText(image,str(is_left_shoulder_correct),
    #                         (380,40),
    #                         cv2.FONT_HERSHEY_TRIPLEX,0.5,(205,116,24),1,cv2.LINE_AA)

    #                 # elbow Data
    #                 cv2.putText(image,'elbow',(470,12),
    #                         cv2.FONT_HERSHEY_TRIPLEX,0.5,(238,121,159),1,cv2.LINE_AA)
    #                 cv2.putText(image,str(is_left_elbow_correct),
    #                         (470,40),
    #                         cv2.FONT_HERSHEY_TRIPLEX,0.5,(238,121,159),1,cv2.LINE_AA)

    #                 # wrist Data
    #                 cv2.putText(image,'wrist',(565,12),
    #                         cv2.FONT_HERSHEY_TRIPLEX,0.5,(0,69,255),1,cv2.LINE_AA)
    #                 cv2.putText(image,str(is_left_wrist_correct),
    #                         (565,40),
    #                         cv2.FONT_HERSHEY_TRIPLEX,0.5,(0,69,255),1,cv2.LINE_AA)

    #                 #visualize right side angles on rectangle
    #                  # shoulder Data
    #                 cv2.putText(image,'shoulder',(360,12),
    #                             cv2.FONT_HERSHEY_TRIPLEX,0.5,(205,116,24),1,cv2.LINE_AA)
    #                 cv2.putText(image,str(is_right_shoulder_correct),
    #                             (380,60),
    #                             cv2.FONT_HERSHEY_TRIPLEX,0.5,(205,116,24),1,cv2.LINE_AA)

    #                         # elbow Data
    #                 cv2.putText(image,'elbow',(470,12),
    #                             cv2.FONT_HERSHEY_TRIPLEX,0.5,(238,121,159),1,cv2.LINE_AA)
    #                 cv2.putText(image,str(is_right_elbow_correct),
    #                             (470,60),
    #                             cv2.FONT_HERSHEY_TRIPLEX,0.5,(238,121,159),1,cv2.LINE_AA)

    #                         # wrist Data
    #                 cv2.putText(image,'wrist',(565,12),
    #                             cv2.FONT_HERSHEY_TRIPLEX,0.5,(0,69,255),1,cv2.LINE_AA)
    #                 cv2.putText(image,str(is_right_wrist_correct),
    #                             (565,60),
    #                             cv2.FONT_HERSHEY_TRIPLEX,0.5,(0,69,255),1,cv2.LINE_AA)

     ####################################################################################################               

    #                 cv2.putText(image,str(Angles['left_shoulder_angle']),
    #                             (430,40),
    #                             cv2.FONT_HERSHEY_TRIPLEX,0.5,(205,116,24),1,cv2.LINE_AA)


    #                 cv2.putText(image,str(Angles['left_elbow_angle']),
    #                             (517,40),
    #                             cv2.FONT_HERSHEY_TRIPLEX,0.5,(238,121,159),1,cv2.LINE_AA)


    #                 cv2.putText(image,str(Angles['left_wrist_angle']),
    #                             (608,40),
    #                             cv2.FONT_HERSHEY_TRIPLEX,0.5,(0,69,255),1,cv2.LINE_AA)


    #                 cv2.putText(image,str(Angles['right_shoulder_angle']),
    #                             (430,60),
    #                             cv2.FONT_HERSHEY_TRIPLEX,0.5,(205,116,24),1,cv2.LINE_AA)


    #                 cv2.putText(image,str(Angles['right_elbow_angle']),
    #                             (517,60),
    #                             cv2.FONT_HERSHEY_TRIPLEX,0.5,(238,121,159),1,cv2.LINE_AA)


    #                 cv2.putText(image,str(Angles['right_wrist_angle']),
    #                             (608,60),
    #                             cv2.FONT_HERSHEY_TRIPLEX,0.5,(0,69,255),1,cv2.LINE_AA)




    #                else :
    #                        front_side = 'RIGHT'

    #                        print(f'front_side : {front_side}')



                    #Feedbacks
                    #All the feedbacks about shoulders
                    #print(f'feedback :{stage_and_state["feedback"]}')

                    if Angles['left_shoulder_angle'] > Easy_Body_treshs['shoulder_correct_range'][1] and Angles['right_shoulder_angle'] > Easy_Body_treshs['shoulder_correct_range'][1] :
                        
                        
#                             feedback_show('image, close your shoulders',shoulders_mp3) 

                            rounded_rectangle(image,90,275,240,45,20,COLORS['dark_orange'])

                            cv2.putText(image,'close your shoulders !',(100,300),
                                        cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,0,0),1,cv2.LINE_AA)
                            #if s2 == 0 :
                            
                            counters['feedback_distance_counter'] += 1
                            
                            if stage_and_state['feedback'] != 'close your shoulders' :
                                    if counters['feedback_distance_counter'] > another_treshs['feedback_distance_tresh'] :

                                        #play_sound('close your shoulders',shoulders_mp3)
                                        shoulders_mp3.play()
                                        stage_and_state['feedback'] = 'close your shoulders'
                                        counters['feedback_distance_counter'] = 0 
                                        



                    elif Angles['left_shoulder_angle'] > Easy_Body_treshs['shoulder_correct_range'][1] and Angles['right_shoulder_angle'] < Easy_Body_treshs['shoulder_correct_range'][1] :

                        #play sounds
                        #if s2 == 0 :


                        if stage_and_state['feedback'] != 'close your left shoulder' :
                                if counters['feedback_distance_counter'] > another_treshs['feedback_distance_tresh'] :

                                    #play_sound('close your left shoulder',left_shoulder_mp3)
                                    counters['feedback_distance_counter'] = 0 
                                    left_shoulder_mp3.play()
                                    stage_and_state['feedback'] = 'close your left shoulder'

                        counters['feedback_distance_counter'] += 1


                        rounded_rectangle(image,90,275,240,45,20,COLORS['dark_orange'])

                        cv2.putText(image,'close your left shoulder !',(100,300),
                                     cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,0,0),1,cv2.LINE_AA)



                    elif Angles['left_shoulder_angle'] < Easy_Body_treshs['shoulder_correct_range'][1] and Angles['right_shoulder_angle'] > Easy_Body_treshs['shoulder_correct_range'][1] :

                         #play sounds
                        #if s2 == 0 :


                        if stage_and_state['feedback'] != 'close your right shoulder' :
                                if counters['feedback_distance_counter'] > another_treshs['feedback_distance_tresh'] :

                                    #play_sound('close your right shoulder',right_shoulder_mp3)
                                    counters['feedback_distance_counter'] = 0 
                                    right_shoulder_mp3.play()
                                    stage_and_state['feedback'] = 'close your right shoulder'

                        counters['feedback_distance_counter'] += 1

                        rounded_rectangle(image,90,275,240,45,20,COLORS['dark_orange'])
                        cv2.putText(image,'close your right shoulder !',(100,300),
                                     cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,0,0),1,cv2.LINE_AA)




            #All the feedbacks about elbows

                    elif Angles['left_elbow_angle'] > Easy_Body_treshs['l_elbow_correct_range'][1] and Angles['right_elbow_angle'] > Easy_Body_treshs['r_elbow_correct_range'][1] :

                         #play sounds
                        #if s2 == 0 :


                        if stage_and_state['feedback'] != 'Close the elbows a little' :
                                if counters['feedback_distance_counter'] > another_treshs['feedback_distance_tresh'] :

                                    #play_sound('close the elbows a little',close_elbows)
                                    counters['feedback_distance_counter'] = 0 
                                    close_elbows_mp3.play()
                                    stage_and_state['feedback'] = 'Close the elbows a little'

                        counters['feedback_distance_counter'] += 1

                        rounded_rectangle(image,90,275,240,45,20,COLORS['dark_orange'])

                        cv2.putText(image,'Close the elbows a little !',(100,300),
                                     cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,0,0),1,cv2.LINE_AA)




                    elif Angles['left_elbow_angle'] > Easy_Body_treshs['l_elbow_correct_range'][1] and Angles['right_elbow_angle'] < Easy_Body_treshs['r_elbow_correct_range'][1] :

                        #play sounds
                        #if s2 == 0 :


                        if stage_and_state['feedback'] != 'Close your left elbow' :
                                if counters['feedback_distance_counter'] > another_treshs['feedback_distance_tresh'] :

                                    #play_sound('close your left elbow',close_left_elbow_mp3)
                                    counters['feedback_distance_counter'] = 0 
                                    close_left_elbow_mp3.play()
                                    stage_and_state['feedback'] =  'Close your left elbow'
                                    

                        counters['feedback_distance_counter'] += 1


                        rounded_rectangle(image,90,275,240,45,20,COLORS['dark_orange'])

                        cv2.putText(image,'Close your left elbow !',(100,300),
                                     cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,0,0),1,cv2.LINE_AA)




                    elif Angles['left_elbow_angle'] < Easy_Body_treshs['l_elbow_correct_range'][1] and Angles['right_elbow_angle'] > Easy_Body_treshs['r_elbow_correct_range'][1] :

                        #play sounds
                        #if s2 == 0 :


                        if stage_and_state['feedback'] != 'Close your right elbow' :

                                if counters['feedback_distance_counter'] > another_treshs['feedback_distance_tresh'] :

                                    #play_sound('close your right elbow',close_right_elbow_mp3)
                                    counters['feedback_distance_counter'] = 0 
                                    speech.play()
                                    close_right_elbow_mp3.play()
                                    stage_and_state['feedback'] =  'Close your right elbow'


                        counters['feedback_distance_counter'] += 1

                        rounded_rectangle(image,90,275,240,45,20,COLORS['dark_orange'])

                        cv2.putText(image,'Close your right elbow !',(100,300),
                                     cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,0,0),1,cv2.LINE_AA)






                    elif Angles['left_elbow_angle'] < Easy_Body_treshs['l_elbow_correct_range'][0] and Angles['right_elbow_angle'] < Easy_Body_treshs['r_elbow_correct_range'][0] :

                        #play sounds
                        #if s2 == 0 :


                        if stage_and_state['feedback'] != 'open the elbows a little' :
                                if counters['feedback_distance_counter'] > another_treshs['feedback_distance_tresh'] :

                                    #play_sound('open the elbows a little',open_elbows_mp3)
                                    counters['feedback_distance_counter'] = 0 
                                    open_elbows_mp3.play()
                                    stage_and_state['feedback'] =  'open the elbows a little' 


                        counters['feedback_distance_counter'] += 1

                        rounded_rectangle(image,90,275,240,45,20,COLORS['dark_orange'])

                        cv2.putText(image,'open the elbows a little !',(100,300),
                                     cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,0,0),1,cv2.LINE_AA)





                    elif Angles['left_elbow_angle'] < Easy_Body_treshs['l_elbow_correct_range'][0] and Angles['right_elbow_angle'] > Easy_Body_treshs['r_elbow_correct_range'][0] :

                        #play sounds
                        #if s2 == 0 :


                        if stage_and_state['feedback'] != 'open your left elbow' :
                                if counters['feedback_distance_counter'] > another_treshs['feedback_distance_tresh'] :

                                   #play_sound('open your left elbow',open_left_elbow_mp3)
                                    counters['feedback_distance_counter'] = 0 
                                    open_left_elbow_mp3.play()
                                    stage_and_state['feedback'] =  'open your left elbow'



                        counters['feedback_distance_counter'] += 1

                        rounded_rectangle(image,90,275,240,45,20,COLORS['dark_orange'])

                        cv2.putText(image,'open your left elbow',(100,300),
                                     cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,0,0),1,cv2.LINE_AA)


                    elif Angles['left_elbow_angle'] > Easy_Body_treshs['l_elbow_correct_range'][0] and Angles['right_elbow_angle'] < Easy_Body_treshs['r_elbow_correct_range'][0] :

                        #play sounds
                        #if s2 == 0 :


                        if stage_and_state['feedback'] != 'open your right elbow' :
                                 if counters['feedback_distance_counter'] > another_treshs['feedback_distance_tresh'] :

                                  # play_sound('open your right elbow',open_right_elbow_mp3)
                                    counters['feedback_distance_counter'] = 0 
                                    open_right_elbow_mp3.play()
                                    stage_and_state['feedback'] =  'open your right elbow'


                        counters['feedback_distance_counter'] += 1


                        rounded_rectangle(image,90,275,240,45,20,COLORS['dark_orange'])

                        cv2.putText(image,'open your right elbow !',(100,300),
                                     cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,0,0),1,cv2.LINE_AA)


                    ####################################################################################################################


                    #print(f'sound_counters{counters["feedback_distance_counter"]}')
                    # Determine correctness of the exercise
                    # curl counter Logic

                    #print(f'state sequnece : {state_sequence}')
                    if Angles['left_shoulder_angle'] < another_treshs['down_tresh'] and Angles['right_shoulder_angle'] < another_treshs['down_tresh'] :


                        if stage_and_state['stage'] =='Down' :

                            counters['first_speed_counter'] += 1
                            counters['second_speed_counter'] = counters['first_speed_counter']
                            counters['down_stage_counter'] += 1

                            if not is_left_elbow_correct or not is_right_elbow_correct or not is_left_shoulder_correct or not is_right_shoulder_correct :

                                stage_and_state['False_state_sequence'].append(False)


                        stage_and_state['stage'] = 'Down'  





                    elif Angles['left_shoulder_angle']> another_treshs['up_tresh'] and Angles['right_shoulder_angle'] > another_treshs['up_tresh'] and stage_and_state['stage'] == 'Down' :

                        counters['down_stage_counter'] = 0

                        stage_and_state['stage'] = 'Up'  



                        if not is_left_elbow_correct and not is_right_elbow_correct and not is_left_shoulder_correct and not is_right_shoulder_correct  :

                            stage_and_state['False_state_sequence'].append(False)


                        if len(stage_and_state['False_state_sequence']) == 0 :
                                counters['correct']+= 1
                                stage_and_state['False_state_sequence'].clear()
                                counters['num_correct_counter'] += 1
                                
                                
                            
                                
                                
#                                 draw_pose (image ,results ,COLORS['green'],mp_drawing,mp_pose)
#                                 stage_and_state['pose_color'] = 'green'
#                                 counters['pose_color_counter'] = 0
                                
                                

                        else:
                            counters['incorrect']+= 1
                            stage_and_state['False_state_sequence'].clear()
                            

                        

                    #progress bar 
                
                    if counters['num_correct_counter'] > 0:
                        if counters['num_correct_counter'] == 1:
                            cv2.line(image, (p1, p2), (p3, p4), COLORS['orange_red'], 3)
                        elif counters['num_correct_counter'] == 2:
                            cv2.line(image, (p1, p2), ((p3 + number_correct, p4)), COLORS['orange_red'], 3)
                        else:
                            cv2.line(image, (p1, p2), ((p3 + (counters['num_correct_counter'] - 1) * number_correct, p4)), COLORS['orange_red'], 3)
                    #print(f'number of correct counter: {counters["num_correct_counter"]}')

                    
                    
                    
                    
                    
                    #print(f'speed counter : {speed_counter}')
                    if stage_and_state['stage'] == 'Up' :

                        #detect and visualize speed of exercise
                        if counters['second_speed_counter'] > another_treshs['speed_tresh'][1] :

                                rounded_rectangle(image,395,430,305,40,20,COLORS['dark_orange'])

                                cv2.putText(image,"you should be faster!",(415,457),
                                cv2.FONT_HERSHEY_TRIPLEX,0.5,(0,0,0),1,cv2.LINE_AA)

                        elif counters['second_speed_counter'] < another_treshs['speed_tresh'][0] :

                                rounded_rectangle(image,395,430,305,40,20,COLORS['dark_orange'])

                                cv2.putText(image,"you should be slower!",(415,457),
                                cv2.FONT_HERSHEY_TRIPLEX,0.5,(0,0,0),1,cv2.LINE_AA)

                        counters['first_speed_counter'] = 0

                else :
                    
#                    feedback_show(image, 'please be front of camera' ,be_front_mp3)
                    rounded_rectangle(image,15,430,270,40,20,COLORS['dark_orange'])

                    cv2.putText(image,'please be front of camera',(25,455),
                    cv2.FONT_HERSHEY_COMPLEX,0.5,(0,0,0),1,cv2.LINE_AA)
                    #if s2 == 0 :
                    stage_and_state['front_stage'] = 'NOT FRONT'

                    if stage_and_state['feedback'] != 'please be front of camera' :

                            #play_sound('please be front of camera',be_front_mp3)
                            counters['feedback_distance_counter'] = 0 
                            be_front_mp3.play()
                            stage_and_state['feedback'] =  'please be front of camera'






#                 print(f'last feedback : {stage_and_state["feedback"]}')
#                 print(f'feed back distance counter : {counters["feedback_distance_counter"]}')


        ################################################################################################


        #detect InActive time

                if counters['down_stage_counter'] > another_treshs['inactive_tresh'] : 

                    counters['correct'] = 0
                    counters['incorrect'] = 0
                    counters['num_correct_counter'] = 0

                    rounded_rectangle(image,220,85,225,40,20,COLORS['dark_orange'])
                    cv2.putText(image,' INACTIVE TIME !',(245,110),
                                 cv2.FONT_HERSHEY_COMPLEX,0.6,(0,0,0),1,cv2.LINE_AA)
#                     if stage_and_state['feedback'] != 'INACTIVE TIME' :
#                         if counters['feedback_distance_counter'] > another_treshs['feedback_distance_tresh'] :

                            #play_sound('INACTIVE TIME !',inanctive_time_mp3)
#                             counters['feedback_distance_counter'] = 0 
#                             inanctive_time_mp3.play()
#                             stage_and_state['feedback'] =  'INACTIVE TIME'

                    
##########################################################################################################

                #visualize pose on body realtime
    
    
                #counters['pose_color_counter'] += 1
        
                if not is_left_elbow_correct or not is_right_elbow_correct or not is_left_shoulder_correct or not is_right_shoulder_correct  :
                            #render detections
                        #DRAW POSE LANDMARKS ON IMAGE
#                     if stage_and_state['pose_color'] == 'green' :
#                         if  counters['pose_color_counter'] < 9 :
                    draw_pose (image ,results ,COLORS['red'],mp_drawing,mp_pose)
                    stage_and_state['pose_color'] = 'red'
#                     else :
#                             draw_pose (image ,results ,COLORS['red'],mp_drawing,mp_pose)
#                             stage_and_state['pose_color'] = 'red'
                
                        
                else :
#                     if stage_and_state['pose_color'] == 'green' :
#                         if counters['pose_color_counter'] < 9  :
                    draw_pose(image,results , COLORS['dark_orange'],mp_drawing,mp_pose)
                    stage_and_state['pose_color'] = 'dark_orange'
#                     else :
#                             draw_pose (image ,results ,COLORS['dark_orange'],mp_drawing,mp_pose)
#                             stage_and_state['pose_color'] = 'dark_orange'
                



        #################################################################################################


            except :

                        pass
                
            
            # DISPLAY IMAGE WITH POSE ESTIMATION OVERLAY
            #cv2.imshow('BEHYAN', image)
            BEHYAN_PALCE.image(image, channels="BGR")
            if counters['num_correct_counter'] == another_treshs['num_correct_tresh'] :
                break
                
            
#             if cv2.waitKey(10) & 0xFF == ord('q'):
#                 break


    cap.release()
    cv2.destroyAllWindows()




BEHYAN_PALCE = st.empty()

def start_button_func():
    st.write('Standing Dumbbell Lateral Raise exercise')
    main_procces ()
    
    
    
    

# def start_training_page () :
    
#     st.write('NOTE : Please stand in front of the camera and keep a minimum distance of one and a half meters from the camera so that your body parts are completely in the frame.')
    
#     st.title('Start Standing Dumbbell Training')
    
#     start_lable_damble = 'start dumbell'
#     start_button_damble = st.button(start_lable_damble)
    
#     if start_button_damble :
#             start_button_func()
    
    
#     st.title('Start Squat Training')
    
#     start_lable_squat = 'start squat'
#     start_button_squat = st.button(start_lable_squat)
    
#     if start_button_squat :
#             start_button_func()
    
    
def Standing_Dumbbell_page():
    st.title('نشر از جانب دو دست / Lateral Raise Dumbbell')
    
    
    # Display an image
    st.image('files/Standing Dumbbell image.PNG', use_column_width=True)
    
    st.title('عضلات هدف :دلتوئید میانی / Middle Deltoid')
 
    st.write('عضلات کمک کننده :')
    st.write('فوق خاری / Supraspinatus ')
    st.write('دلتوئید قدامی / Anterior Deltoid ')
    st.write('دندانه ای قدامی / Serratus Anterior ')
    st.write('ذوزنقه ای میانی / Lower Trapezius')
    st.write('ذوزنقه ای بالایی/ Upper Trapezius')
    st.write('عضلات ثبات دهنده : ')
    st.write('عضلات شکم / Abdominal Muscles')
    st.write('بالابرنده کتف / Levator Scapulae')
    st.write('نگهدار پشت / Erector Spinae')
    st.write('ذوزنقه ای میانی / Middle Trapezius ')
    st.write('ذوزنقه ای بالایی/ Upper Trapezius ')
    st.write('محدودیت حرکت :')
    st.write('افرادی که دامنه حرکتی آنها محدود شده است و یا دچار گیر افتادگی شانه / Impingement هستند در انجام این حرکت دچار مشکل میشوند')
    st.write('برای افرادی که دچار شانه یخ زده / Frozen Shoulder هستند انجام این حرکت همراه با درد است و توصیه نمیشود.')
    st.write('هدف تمرین')
    
    st.write('یک تمرین تک مفصله و قدرتی برای تقویت سرشونه ها هدف این تمرین تقویت عضلات دلتوئید مخصوصن دلتوئید میانی هست')
    
    st.video('files/lateral raise mucsle.mp4')
    # Embed a YouTube video
 #   st.video('files/damble_video.mp4')
    
    
    st.write('NOTE :لطفا جلوی دوربین بایستید و حداقل یک و نیم متر از دوربین فاصله بگیرید تا اعضای بدن شما کاملا در کادر قرار بگیرد.همچنین سعی کنید در محیطی با نور مناسب تمرین کنید سپاس.')
    
    st.title('شروع تمرین نشر از جانب دو دست  : ')
    
    start_lable_damble = 'شروع تمرین'
    start_button_damble = st.button(start_lable_damble)
    
    if start_button_damble :
            start_button_func()
   

    
        
def squat_page() :
    st.title('تمرین اسکات')
    
    # Display an image
    st.image('files/Squat-au-poids-du-corps.PNG', use_column_width=True)
    
    st.title('عضلات هدف :')
    st.write('عضلات کمکی')
    st.write('همسترینگ نعلی و دوقلو')
    st.write('عضلات همسترینگ / Hamstrings')
    st.write('دوقلو / Gastrocnemius')
    st.write('نعلی / Soleus ')
    st.write('عضلات ثبات دهنده :')
    st.write('عضلات شکم / Abdominal Muscles')
    st.write('نگهدار پشت / Erector Spinae ')
    st.write('عضلات کف لگن / Pelvic Diaphragm')
    st.write('دیافراگم / Diaphrag')
    st.write('محدودیت حرکت')
    st.write('افراد مبتلا به هر نوع آسیب زانو، مانند پارگی ACL یا پارگی منیسک')
    st.write('افراد مبتلا به هر نوع آسیب لگن، مانند پارگی لابروم / Hip Labral Tear ، گیرافتادگی مفصل رانی-لگنی Hip Impingement')
    st.write('افراد مبتلا به هر نوع آسیب کمر، مانند فتق دیسک ')
    st.write('هدف تمرین :')
    st.write('یکی از محبوب ترین تمرینات قدرتی که حتی بدون داشتن تجهیزات و فقط با وزن بدن انجام میشه Air Squat هست ')
    st.write('هدف اصلی از این تمرین چند مفصله، تقویت عضلات ران و باسن هست ولی به دلیل درگیر کردن 10 عضله ای که قبلا اشاره شد، میتونه برای تمام بدن مفید باشد')
    st.write('البته اگه صحیح انجام بشه!')
    
    
    
    
    st.video('files/squat_2.mp4')
    # Embed a YouTube video
#    st.video('files/squat.mp4')
    
    
    st.write('لطفا جلوی دوربین بایستید و حداقل یک و نیم متر از دوربین فاصله بگیرید تا اعضای بدن شما کاملا در کادر قرار بگیرد.همچنین سعی کنید در محیطی با نور مناسب تمرین کنید سپاس.')
    
    
    st.title('شروع تمرین اسکات : ')
    
    start_lable_squat = 'شروع تمرین'
    start_button_squat = st.button(start_lable_squat)
    
    if start_button_squat :
            start_button_func()
    # Add a button to start training
#     if st.button('Start Training'):
#         page = 'Start Training'
#         pages[page]()
    

    
pages = {
    'نشر از جانب دو دست': Standing_Dumbbell_page,
    'اسکات' : squat_page,
#    'start training' :start_training_page
}

st.sidebar.title('Menu')
page = st.sidebar.radio('Select a page:', list(pages.keys()))

pages[page]()


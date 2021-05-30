from darkflow.net.build import TFNet
import cv2
import numpy as np
import matplotlib.pyplot as plt
import os 

threshold = 0.02
options = {"pbLoad": "built_graph/tiny-yolo-lab9.pb",
            "threshold": threshold,
           "metaLoad": "built_graph/tiny-yolo-lab9.meta" 
           }
# eval_path = 'test_img/'         
eval_path = '/Users/samuelyu/Downloads/Lab09_student/demo_video/demo.wmv'         

tfnet = TFNet(options)



def boxing(original_img, predictions, thre):
    newImage = np.copy(original_img)

    for result in predictions:
        top_x = result['topleft']['x']
        top_y = result['topleft']['y']

        btm_x = result['bottomright']['x']
        btm_y = result['bottomright']['y']

        confidence = result['confidence']
        label = result['label'] + " " + str(round(confidence, 2))

        if confidence > thre:
            newImage = cv2.putText(newImage, label, (top_x, top_y-5), cv2.FONT_HERSHEY_SIMPLEX ,1, (0, 255, 0), 1, cv2.LINE_AA)
            newImage = cv2.rectangle(newImage, (top_x, top_y), (btm_x, btm_y), (255,0,0), 3)
            
            
    return newImage


# cap = cv2.VideoCapture(0)
cap = cv2.VideoCapture(eval_path)

# fourcc = cv2.VideoWriter_fourcc(*'XVID')
fourcc = cv2.VideoWriter_fourcc('M','J','P','G')
# out = cv2.VideoWriter('output.avi', fourcc)
out = cv2.VideoWriter('output.avi', fourcc, 10.0, (640, 360))
# out = cv2.VideoWriter('output.avi', fourcc, 20.0, (640, 360))

while cap.isOpened():
    # Read the frame
    ret, frame = cap.read()
    cv2.imshow("result", frame)
    cv2.waitKey(33)
    result = tfnet.return_predict(frame)

    if len(result)!=0:
        out.write(boxing(frame, result, threshold))
    else:
        out.write(frame)
        print("Nothing detected")




# images_ls = [f for f in os.listdir(eval_path) if f.endswith('.jpg')]

# for img in images_ls:
#     path = eval_path+img
#     imgcv = cv2.imread(path)
#     result = tfnet.return_predict(imgcv)

#     if len(result)!=0:
#         cv2.imshow("result", boxing(imgcv, result, threshold))
#         cv2.waitKey(0)
#     else:
#         print("Nothing detected")


# -*-coding:utf-8-*-
__author__ = 'jzhizhi'

import os
import random

f=open('D:\\zhihan\\traffic_signs_detection\\yolov3\\keras-yolo3\\train_data\\set1\\label_select_no_path_test.csv','r')

path='D:\\zhihan\\traffic_signs_detection\\yolov3\\keras-yolo3\\train_data\\set1\\train_select\\'
train=open('D:\\zhihan\\traffic_signs_detection\\yolov3\\keras-yolo3\\train_data\\set1\\label_select_num_test.txt','w');

#val_full=open('E:\\Zhihan\\yolov3\\keras-yolo3\\left_train_data2007_val.txt','w');
#test_full=open('2007_test.txt','w');

classes=["no_parking","turn_left","turn_right","uturn","bg","bg_red_stop","bg_blue_arrow"];
# no_parking,0
# turn_left,1
# turn_right,2
# uturn,3
# bg,4
# bg_red_stop,5
# bg_blue_arrow,6
dic_num={"no_parking":0,"turn_left":0,"turn_right":0,"uturn":0,"bg":0,"bg_red_stop":0,"bg_blue_arrow":0}
dic_s={"no_parking":0,"turn_left":0,"turn_right":0,"uturn":0,"bg":0,"bg_red_stop":0,"bg_blue_arrow":0}
ss_np=[]
ss_tl=[]
ss_tr=[]
ss_ut=[]
ss_bg=[]
# np=open('D:\\zhihan\\traffic_signs_detection\\yolov3\\keras-yolo3\\train_data\\set1\\np.txt','w')
# tl=open('D:\\zhihan\\traffic_signs_detection\\yolov3\\keras-yolo3\\train_data\\set1\\tl.txt','w')
# tr=open('D:\\zhihan\\traffic_signs_detection\\yolov3\\keras-yolo3\\train_data\\set1\\tr.txt','w')
# ut=open('D:\\zhihan\\traffic_signs_detection\\yolov3\\keras-yolo3\\train_data\\set1\\ut.txt','w')
# bg=open('D:\\zhihan\\traffic_signs_detection\\yolov3\\keras-yolo3\\train_data\\set1\\bg.txt','w')
for line in f:
	result=line.split(',')
	name=result[0]
	x1=result[1]
	y1=result[2]
	x2=result[3]
	y2=result[4]

	s=(int(x2)-int(x1))*(int(y2)-int(y1))

	cl=result[5]
	cl=cl.rstrip('\n')
	#n=random.randrange(0,10)
	# if(cl=="bg"):
	# 	continue
	dic_num[cl]+=1
	dic_s[cl]+=s
	c=classes.index(cl)
	# if(c==0):
	# 	ss_np.append(s)
	# 	np.write(str(round(s))+"\n")
	# elif(c==1):
	# 	ss_tl.append(s)
	# 	tl.write(str(round(s))+"\n")
	# elif(c==2):
	# 	ss_tr.append(s)
	# 	tr.write(str(round(s))+"\n")
	# elif(c==3):
	# 	ss_ut.append(s)
	# 	ut.write(str(round(s))+"\n")
	# elif(c==4 or c==5 or c==6):
	# 	ss_bg.append(s)
	# 	bg.write(str(round(s))+"\n")
	
	#if(n<8):
	
	train.write(path+name+","+x1+","+y1+","+x2+","+y2+","+str(c)+"\n")
	
	#else:
	#	val_full.write(path+name+","+x1+","+y1+","+x2+","+y2+","+str(c)+"\n")
	# else:
	# 	test_full.write(path+name+","+x1+","+y1+","+x2+","+y2+","+str(cl)+"\n")
	#txtfile=open('./label/%s.txt'%(name_nojpg),'w')
	#txtfile.write("0"+" "+x1+" "+y1+" "+str(w)+" "+str(h)+'\n')

f.close()
# np.close()
# tl.close()
# tr.close()
# ut.close()
# bg.close()

#train.close()
# print(dic_num)
# print(dic_s)
# print(sum(ss_np)/len(ss_np))
# print(sum(ss_tl)/len(ss_tl))
# print(sum(ss_tr)/len(ss_tr))
# print(sum(ss_ut)/len(ss_ut))
# print(sum(ss_bg)/len(ss_bg))
#val_full.close()
#test_full.close()
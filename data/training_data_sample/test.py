# -*-coding:utf-8-*-
__author__ = 'jzhizhi'

import os
import random

f=open('D:\\zhihan\\yolov3\\keras-yolo3\\VOCdevkit\\VOC2007\\label_simple.txt','r')

#val_full=open('E:\\Zhihan\\yolov3\\keras-yolo3\\left_train_data2007_val.txt','w');
#test_full=open('2007_test.txt','w');

classes=["turn_left","turn_right","uturn","no_parking","bg"];
dic={"turn_left":0,"turn_right":0,"uturn":0,"no_parking":0,"bg":0}

for line in f:
	result=line.split(',')
	name=result[0]
	x1=result[1]
	y1=result[2]
	x2=result[3]
	y2=result[4]
	cl=result[5]
	cl=cl.rstrip('\n')
	#n=random.randrange(0,10)
	# if(cl=="bg"):
	# 	continue
	dic[cl]=dic[cl]+1
	#if(n<8):
	#else:
	#	val_full.write(path+name+","+x1+","+y1+","+x2+","+y2+","+str(c)+"\n")
	# else:
	# 	test_full.write(path+name+","+x1+","+y1+","+x2+","+y2+","+str(cl)+"\n")
	#txtfile=open('./label/%s.txt'%(name_nojpg),'w')
	#txtfile.write("0"+" "+x1+" "+y1+" "+str(w)+" "+str(h)+'\n')
print(dic)
f.close()

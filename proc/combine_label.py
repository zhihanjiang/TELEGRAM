# -*-coding:utf-8-*-
__author__ = 'jzhizhi'

import os
import random

f1=open('D:\\zhihan\\traffic_signs_detection\\yolov3\\keras-yolo3\\train_data\\set1\\label_select_no_path.csv','r')
f2=open('D:\\zhihan\\traffic_signs_detection\\yolov3\\keras-yolo3\\train_data\\set2\\label_tt100k_all_nopath.txt','r')

path1='D:\\zhihan\\traffic_signs_detection\\yolov3\\keras-yolo3\\train_data\\set1\\train_select\\'
path2='D:\\zhihan\\traffic_signs_detection\\yolov3\\keras-yolo3\\train_data\\set2\\all\\'

train=open('D:\\zhihan\\traffic_signs_detection\\yolov3\\keras-yolo3\\train_data\\label.txt','w');

classes1=["no_parking","turn_left","turn_right","uturn","bg","bg_red_stop","bg_blue_arrow"];
# no_parking,0
# turn_left,1
# turn_right,2
# uturn,3
# bg,4
# bg_red_stop,5
# bg_blue_arrow,6

for line in f1:
	result=line.split(',')
	name=result[0]
	x1=result[1]
	y1=result[2]
	x2=result[3]
	y2=result[4]
	cl=result[5]
	cl=cl.rstrip('\n')
	c=classes1.index(cl)
	train.write(path1+name+","+x1+","+y1+","+x2+","+y2+","+str(c)+"\n")

classes2=["pn","p23","p19","p5"]
class_2=open('D:\\zhihan\\traffic_signs_detection\\yolov3\\keras-yolo3\\train_data\\set2\\class_list_all.txt','r')
dic={};
for line in class_2:
	result=line.split(',')
	cl=result[0]
	num=result[1].rstrip('\n')
	dic[cl]=int(num)

temp=[]
for line in f2:
	result=line.split(',')
	name=result[0]
	x1=result[1]
	y1=result[2]
	x2=result[3]
	y2=result[4]
	cl=result[5]
	cl=cl.rstrip('\n')
	if dic[cl]<100:
		continue
	if cl in classes2:
		c=classes2.index(cl)
	else:
		if cl in temp:
			c=temp.index(cl)+7
		else:
			temp.append(cl)
			c=temp.index(cl)+7

	train.write(path2+name+","+x1+","+y1+","+x2+","+y2+","+str(c)+"\n")

class_list=open('D:\\zhihan\\traffic_signs_detection\\yolov3\\keras-yolo3\\train_data\\class_list.csv','w');
voc_classes=open('D:\\zhihan\\traffic_signs_detection\\yolov3\\keras-yolo3\\train_data\\voc_classes.txt','w');
for cl in classes1:
	class_list.write(cl+','+str(classes1.index(cl))+'\n');
	voc_classes.write(cl+'\n');
for cl in temp:
	class_list.write(cl+','+str(temp.index(cl)+7)+'\n')
	voc_classes.write(cl+'\n');

f1.close()
f2.close()
class_2.close()


train.close()
class_list.close()
#val_full.close()
#test_full.close()
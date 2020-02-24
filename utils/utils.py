# coding:utf-8
# TODO:
# 		创建训练及测试所需的文件

import glob
import os, sys, shutil
import random


data_path = "/home/data_ssd/lcf/VCTK_closeset"
"""
####################################################
# 生成提取MFCC特征所需的scp文件
with open("VCTK_test_htk_MFCC.lst", "w") as f:
	for wav in glob.glob("VCTK_test/*/*.wav"):
		wav_path = data_path + "/" + wav
		mfcc_path = data_path + "/" + wav
		mfcc_path = mfcc_path.replace("VCTK_train", "VCTK_train_htk_MFCC")
		mfcc_path = mfcc_path.replace(".wav", ".mfcc")
		f.write("{} {}\n".format(wav_path, mfcc_path))
"""

"""
for spk in glob.glob("VCTK_test/*"):
	if not os.path.exists("VCTK_test_htk_MFCC/" + spk):
		os.makedirs("VCTK_test_htk_MFCC/" + spk)
"""


####################################################
# make speaker_model_maps.lst and trials.lst
feats_list, spk_list = [], []
with open("../data_lst/speaker_model_maps.lst", "w") as f:
	for spk in glob.glob(data_path+"/VCTK_test_htk_MFCC/*"):
		# 随机选取30句作为注册
		pools = glob.glob(spk+"/*")
		sample_mfcc = random.sample(pools, 30)
		for mfcc in sample_mfcc:			
			f.write("{} {}\n".format(spk.split("/")[-1], mfcc))
			pools.remove(mfcc)
		
		# 将未用作注册的语句保存起来, 用来做测试
		feats_list.append(pools)
		spk_list.append(spk.split("/")[-1])

f_trials = open("../data_lst/trials.lst", "w")	
for spk_idx, spk in enumerate(spk_list):
	for feat_idx, feats in enumerate(random.sample(feats_list, int(len(feats_list)/2))):
		if spk_idx == feat_idx:
			label = "target"
			for feat in feats:
				f_trials.write("{} {} {}\n".format(spk, feat, label))
		else:
			label = "impostor"
			for feat in feats:
				f_trials.write("{} {} {}\n".format(spk, feat, label))
f_trials.close()


"""
######################################################
# make speaker_model_maps.lst and trials.lst like vox1 format
spk_list = []
feats_list = []
f_test_like_vox = open(data_path + "/VCTK_test/test.txt")
speaker_model_file = open("../data_lst/speaker_model_maps_like_vox1_.lst", "w")
trials_file = open("../data_lst/trials_like_vox1.lst", "w")
for line in f_test_like_vox.readlines():
	line = line.strip()
	label, enro, test = line.split(" ")
	enro_mfcc = data_path+"/VCTK_test_htk_MFCC/"+enro.replace(".wav", ".mfcc")
	speaker_model_file.write("{} {}\n".format(enro, enro_mfcc))

	if label == "1":
		label_ = "target"
	else:
		label_ = "impostor"
	test_mfcc = data_path+"/VCTK_test_htk_MFCC/"+test.replace(".wav", ".mfcc")
	trials_file.write("{} {} {}\n".format(enro, test_mfcc, label_))
f_test_like_vox.close()
speaker_model_file.close()
trials_file.close()

# 去掉speaker_model_maps_like_vox1.lst中重复的行
command = "cat ../data_lst/speaker_model_maps_like_vox1_.lst | uniq > ../data_lst/speaker_model_maps_like_vox1.lst"
os.system(command)
"""

"""
for mfcc in glob.glob("VCTK_test/*/*.mfcc"):
	dst = "VCTK_test_htk_MFCC/{}/".format(mfcc.split("/")[-2])
	shutil.move(mfcc, dst)
"""

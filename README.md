# 使用MSR-Idendity-toolkit 做GMM-UBM实验的过程记录
speaker recognitiong using GMM-UBM, implementing on MSR-Idendity-toolkit.
### 零、准备工作

下载MSR工具包，该工具包是matlab代码，即`.m`文件，[github地址](<https://github.com/wangwei2009/MSR-Identity-Toolkit-v1.0>)。

下载ALIZE工具包，用于提取HTK格式的MFCC特征，如安装有HTK并会用HTK来提取MFCC特征可忽略，[地址](https://alize.univ-avignon.fr/doc/01_GMM-UBM_system_with_ALIZE3.0.tar.gz)

### 一、提取MFCC特征

由于MSR工具包需要使用htk格式的mfcc特征，而HTK的安装有点复杂，因此这里直接使用ALIZE3.0工具包提取mfcc特征，ALIZE就是使用HTK的HCopy提取特征的，好处是不用安装HTK就可以直接使用HCopy，直接下载ALIZE工具包编译后即可使用。ALIZE下载地址：[点击这里](https://alize.univ-avignon.fr/doc/01_GMM-UBM_system_with_ALIZE3.0.tar.gz)；ALIZE 官网地址：[点击这里](https://alize.univ-avignon.fr/)

##### 用ALIZE的HCopy工具提取mfcc特征的步骤

所用代码为：

```shell
bin/HCopy -C cfg/hcopy_VCTK_mfcc.cfg -T 1 -S VCTK_train_htk.scp
```

代码解释：

- Hcopy工具包的位置在`MFCC_extract_toolkit/01_GMM-UBM_system_with_ALIZE3.0/bin`目录下

- 需要准备mfcc配置文件`hcopy_VCTK_mfcc.cfg`，文件内容如下：

  ```
  #Feature configuration
  SOURCEFORMAT = WAV
  TARGETRATE = 100000.0
  TARGETKIND = MFCC_0_D_A
  WINDOWSIZE = 250000.0
  NUMCEPS = 12
  NUMCHANS = 27
  PREEMCOEF = 0.97
  CEPLIFTER = 22
  ```

- 语音路径及特征保存路径文件`VCTK_train_htk.scp`内容如下：

  ```
  <语音路径> <mfcc特征保存路径>
  /home/data_ssd/lcf/VCTK_closeset/VCTK_train/p293/p293_230.wav /home/data_ssd/lcf/VCTK_closeset/VCTK_train_htk_MFCC/p293/p293_230.mfcc
  ```

生成以上scp文件的脚本在`utils/make_scp.py`

### 二、准备数据

使用MSR工具训练GMM-UBM需要准备三个文件：ubm.lst、speaker_model_maps.lst、trials.lst

- `ubm.lst`：该文件内容为训练UBM模型所需要的所有mfcc特征，每行为一条语音的mfcc特征地址，如下：

  ```
  /home/data_ssd/lcf/VCTK_closeset/VCTK_train_htk_MFCC/p293/p293_230.mfcc
  /home/data_ssd/lcf/VCTK_closeset/VCTK_train_htk_MFCC/p293/p293_339.mfcc
  ...
  ```

- `speaker_model_maps.lst`：该文件内容为用来注册的说话人的mfcc特征地址，格式如下:

  ```
  <spk_id> <mfcc_path>
  p233 /home/data_ssd/lcf/VCTK_closeset/VCTK_test_htk_MFCC/p233/p233_381.mfcc
  p233 /home/data_ssd/lcf/VCTK_closeset/VCTK_test_htk_MFCC/p233/p233_279.mfcc
  ...
  ```

  通常每个说话人注册多条语音，称为说话人模型。

- `trials.lst`：该文件内容为测试样本对，包含注册的说话人模型、测试用例和标签，格式如下

  ```
  <enro_spk_model> <test_utt> <label>
  p233 VCTK_test_htk_MFCC/p233/p233_058.mfcc target
  p233 VCTK_test_htk_MFCC/p233/p233_025.mfcc target
  p233 VCTK_test_htk_MFCC/p227/p227_274.mfcc impostor
  p233 VCTK_test_htk_MFCC/p227/p227_357.mfcc impostor
  ...
  ```

生成以上文件的脚本为：`utils/make_scp.py`

### 三、训练UBM模型

在MSR中只要执行一行代码即可，matlab代码如下

```matlab
ubm = gmm_em(dataList, nmix, final_niter, ds_factor, nworkers);
```

其中dataList为文件`ubm.lst`的地址，这里是`dataList=../data_lst/ubm.lst`

nmix是GMM的高斯分量个数，这里设为`	nmix=512`

final_niter是EM算法的迭代次数，这里设为`final_niter=15`

ds_factor是特征二次采样因子，默认为1

nworkers是CPU核心数，这里是`nworkers=12`

### 四、从UBM中适应说话人模型

原话为 Adapting the speaker models from UBM，我的理解应该是利用注册语句进行注册说话人模型。

主要用到的函数是:

```matlab
gmm_models{spk}=mapAdapt(spk_files, ubm, map_tau, config)
```

这一步需要读入`speaker_model_maps.lst`文件

具体见.m文件

### 五、计算得分（测试）

计算trials测试样本对的得分，返回一个分数列表scores，用到的函数是：

```matlab
scores = score_gmm_trials(gmm_models, test_files, trials, ubm);
```

这一步需要读入`trials.lst`文件

### 六、计算等误率

根据上一步得到的分数和label，计算EER

```matlab
eer = compute_eer(scores, labels, true);
```

完整代码在 `code/demo_gmm_ubm.m`中


在VCTK数据集上的结果：

训练集：89个spk    
测试集：20个spk
训练集和测试集的spk无交集

enro: 每个spk随机选10个utt注册(即用10句从ubm中适应出说话人模型)       
eval：测试集中除去enro集之外的所有utt       
EER:    
256个GMM分量：0.9262%   
512个GMM分量：0.86%     

按照vox1官方提供的voxceleb1_test.txt类似格式组织trials，即使用一句话进行注册。    
256个GMM分量：5.6587%
512个GMM分量：爆内存，放弃测试。

enro: 每个spk随机选30个utt注册(即用10句从ubm中适应出说话人模型)       
eval：测试集中除去enro集之外的所有utt       
EER:    
256个GMM分量：0.5441%   
512个GMM分量：0.4456%     

enro: 每个spk随机选100个utt注册(即用10句从ubm中适应出说话人模型)       
eval：测试集中除去enro集之外的所有utt       
EER:    
256个GMM分量： 
512个GMM分量：0.3272%     


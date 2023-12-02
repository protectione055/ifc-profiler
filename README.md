## 1. 环境配置
### 1.1 首先需要安装conda环境
```
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
chmod +x ./Miniconda3-latest-Linux-x86_64.sh
./Miniconda3-latest-Linux-x86_64.sh
```

### 1.2 安装依赖包
```
conda create --name ifc-test
conda activate ifc-test
conda install --file environment.yml
```

## 2. 使用
 * 样例数据集在bim_models_dataset文件夹
 * 文件说明：
    *  `ifc_profile_util.py`：公用的函数库
    * `ifc_statistic.py`：统计ifc文件中的实体数量
    * `ifc_graph_generator.py`：生成IFC实例关系图
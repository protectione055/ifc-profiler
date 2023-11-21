import re
import os
import ifcopenshell


# 匹配IFC实体的正则表达式
pattern = '''#\d+=(IFC[A-Z]+)\(.*\);'''

# 设置输入路径
projects = ['HRZB']

# 设置输出文件名
result_filename = "IFC_wordlist_siglefile.txt"

# 定义一个迭代器，递归地返回目录下所有IFC文件的路径
def iterate_ifc_directory(input_path):
    for filename in os.listdir(input_path):
            if filename.endswith(".ifc"):
                yield os.path.join(input_path, filename)
            elif os.path.isdir(os.path.join(input_path, filename)):
                for file in iterate_ifc_directory(os.path.join(input_path, filename)):
                    yield file

# 判断一行文本是否为IFC实体
def is_ifc_entity(line):
    match = re.findall(pattern, line)
    if match:
        return True
    else:
        return False

# 数据集总大小, 文件数量, 实体数量
def dataset_profile(dataset_path):
    dataset_size = 0
    file_count = 0
    entity_count = 0
    for ifc_file in iterate_ifc_directory(dataset_path):
        file_count += 1
        dataset_size += os.path.getsize(ifc_file)
        with open(ifc_file, 'r') as f:
            lines = f.readlines()
            for line in lines:
                if is_ifc_entity(line):
                    entity_count += 1
    return dataset_size, file_count, entity_count

# 统计目录下所有Ifc文件中各个实体的数量
def count_project_entity(project_dir):
    entities_dict = {}
    if project_dir.endswith("/"):
        project_dir = project_dir[:-1]

    for file in iterate_ifc_directory(project_dir):
                # print(filename + '\n')
                with open(file, 'r') as f:
                    lines = f.readlines()
                    for line in lines:
                        match = re.findall(pattern, line)
                        if match:
                            entities_dict[match[0]] = entities_dict.get(match[0], 0) + 1
    return entities_dict
    

if __name__ == '__main__':
    result_dir = "result/"
    if os.path.exists(result_dir):
        os.system("rm -rf " + result_dir)
    os.mkdir(result_dir)
    
    for project_dir in projects:
        # 统计项目中每一个实体的数量
        entities_dict = count_project_entity(project_dir)
        with open(result_dir + project_dir + "_count_project_entity.csv", 'w') as result_file:
            sorted_entities = sorted(entities_dict.items(),
                                    key=lambda x: x[1], reverse=True)
            result_file.write("ENTITY,FREQ(#)\n")
            for entity in sorted_entities:
                result_file.write(entity[0] + ',' + str(entity[1]) + '\n')
        
        # 数据集统计
        dataset_size, file_count, entity_count = dataset_profile(project_dir)
        with open(result_dir + "dataset_profile.csv", 'w') as result_file:
            result_file.write("PROJECT, SIZE(MB), FILE(#), ENTITY(#)\n")
            # 转换为MB，保留两位小数
            dataset_size = round(dataset_size / 1024 / 1024, 2)
            # 每隔三位加一个逗号
            result_file.write(project_dir + ", " + str(dataset_size) + ',' + str(file_count) + ',' + str(entity_count) + '\n')
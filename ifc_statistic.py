import re
import os
import ifcopenshell
from ifc_profile_util import *


# 匹配IFC实体的正则表达式
pattern = '''#\d+=(IFC[A-Z]+)\(.*\);'''

# 设置输入路径
proj_dir = 'bim_models_dataset'
# 打印目录下所有文件名，然后路径拼接，返回列表
projects = [proj_dir + '/' + filename for filename in os.listdir(proj_dir)]

# 设置输出文件名
result_filename = "IFC_wordlist_siglefile.txt"

# 数据集总大小, 文件数量, 实体数量
def dataset_profile(dataset_path):
	dataset_size = 0
	file_count = 0
	entity_count = 0
	for ifc_file in iterate_ifc_directory(dataset_path):
		file_count += 1
		dataset_size += os.path.getsize(ifc_file)
		try:
			with open(ifc_file, 'r', errors='ignore') as f:
				lines = f.readlines()
				for line in lines:
					if is_ifc_entity(line):
						entity_count += 1
		except Exception as e:
			print(f"处理{ifc_file}时出错: {e}")
	return dataset_size, file_count, entity_count

# 统计目录下所有Ifc文件中各个实体的数量
def count_project_entity(project_dir):
	entities_dict = {}
	if project_dir.endswith("/"):
		project_dir = project_dir[:-1]

	for file in iterate_ifc_directory(project_dir):
				# print(filename + '\n')
		try:
			with open(file, 'r', errors='ignore') as f:
				lines = f.readlines()
				for line in lines:
					match = re.findall(pattern, line)
					if match:
						entities_dict[match[0]] = entities_dict.get(
							match[0], 0) + 1
		except Exception as e:
			print(f"处理{file}时出错: {e}")
	return entities_dict

# 统计ifc文件中关系实体和非关系实体的数量
def count_vertex_edge(project_dir):
	"""
	Count the number of vertices and edges in the IFC files within the specified project directory.

	Args:
		project_dir (str): The path to the project directory.

	Returns:
		dict: A dictionary containing the count of vertices and edges.
			The dictionary has the following structure: {"vertex": int, "edge": int}.
	"""
	item = {"vertex": 0, "edge": 0}
	for file in iterate_ifc_directory(project_dir):
		print(file)
		# ifcopenshell加载ifc文件
		try:
			ifc_file = ifcopenshell.open(file)
			# 获取所有继承IfcRelationship的实体
			relation = ifc_file.by_type("IfcRelationship")
			item["edge"] += len(relation)
			# 获取所有继承IfcObject和IfcTypeObject的实体
			non_relation = ifc_file.by_type("IfcObject") + ifc_file.by_type("IfcTypeObject")
			item["vertex"] += len(non_relation)
		except Exception as e:
			print(f"处理{file}时出错: {e}")
	return item
	

if __name__ == '__main__':
	result_dir = "result/"
	if os.path.exists(result_dir):
		os.system("rm -rf " + result_dir)
	os.mkdir(result_dir)
	
	first_pass = True
	for project_dir in projects:
		# 执行mkdir -p result_dir + project_dir

		# 1. 统计项目中每一个实体的数量
		entities_dict = count_project_entity(project_dir)
		with open(result_dir + os.path.basename(project_dir) + "_count_project_entity.csv", 'a') as result_file:
			sorted_entities = sorted(entities_dict.items(),
									key=lambda x: x[1], reverse=True)
			result_file.write("ENTITY,FREQ(#)\n")
			for entity in sorted_entities:
				result_file.write(entity[0] + ',' + str(entity[1]) + '\n')
		
		# 2. 数据集统计
		dataset_size, file_count, entity_count = dataset_profile(project_dir)
		with open(result_dir + "dataset_profile.csv", 'a') as result_file:
			if first_pass:
				result_file.write("PROJECT, SIZE(MB), FILE(#), ENTITY(#)\n")
			# 转换为MB，保留两位小数
			dataset_size = round(dataset_size / 1024 / 1024, 2)
			# 每隔三位加一个逗号
			result_file.write(project_dir + ", " + str(dataset_size) + ',' + str(file_count) + ',' + str(entity_count) + '\n')
		
  
		# 3. 统计关系实体和非关系实体的数量
		vertex_edge = count_vertex_edge(project_dir)
		with open(result_dir + "count_vertex_edge.csv", 'a') as result_file:
			if first_pass:
				result_file.write("PROJECT, VERTEX(#), EDGE(#)\n")
			result_file.write(project_dir + ", " + str(vertex_edge["vertex"]) + ',' + str(vertex_edge["edge"]) + '\n')
		first_pass = False
import graph_tool.all as gt
import ifcopenshell
import os
import re


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


# 给定一个IFC文件，返回属性图模型
def ifc_to_property_graph(file):
    ifc_file = ifcopenshell.open(file)
    # 创建一个空图
    graph = gt.Graph(directed=False)
    # 为每个实体创建一个顶点
    for entity in ifc_file:
        if entity.is_a("IfcRelationship"):
            # 获取以Relating为前缀的属性
            attributes = entity.get_info()
            relating_entity = None
            related_entities = None
            for key, value in attributes.items():
                if key.startswith("Relating"):
                    # 获取属性值
                    relating_entity = value
                elif key.startswith("Related"):
                    related_entities = value
            # 如果related_entities是一个列表
            if isinstance(related_entities, tuple):
                for related_entity in related_entities:
                    graph.add_edge(relating_entity.id(), related_entity.id())
            elif isinstance(
                related_entities, ifcopenshell.entity_instance
            ):
                graph.add_edge(relating_entity.id(), related_entities.id())
            else:
                print(type(related_entities))
                print(related_entities)
        else:
            graph.add_vertex(entity.id())
    return graph

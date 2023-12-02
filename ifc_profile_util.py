import graph_tool.all as gt
import ifcopenshell
import os
import re
import random
import matplotlib.pyplot as plt


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


# 三元颜色组合
three_color = ["#ffae49", "#44b7c2", "#024b7a"]


# 输入color_dict生成legend
def draw_legend(color_dict):
    plt.figure(figsize=(5, 5))
    plt.title("图例")
    for entity_type, color in color_dict.items():
        plt.plot([], [], color=color, label=entity_type)
    plt.legend()
    plt.axis("off")
    plt.show()


# 不同类型的实体对应的颜色
color_map = {
    "IfcRelationship": three_color[0],
    "IfcProduct": three_color[1],
    "Others": three_color[2],
}


def ifc_to_property_graph(file):
    """
    Converts an IFC file to a property graph.

    Args:
        file (str): The path to the IFC file.

    Returns:
        graph (Graph): The property graph representing the IFC file.
    """
    ifc_file = ifcopenshell.open(file)
    graph = gt.Graph(directed=False)
    entity_name = graph.new_vp("string")
    graph.vp.name = entity_name
    entity_color = graph.new_vp("string")
    graph.vp.color = entity_color
    entity_type = graph.new_vp("string")
    graph.vp.type = entity_type
    edge_width = graph.new_ep("int")
    graph.ep.width = edge_width
    entity_lists = [entity for entity in ifc_file]
    entity_lists.sort(key=lambda x: x.id())
    graph.add_vertex(entity_lists[-1].id() + 1)
    print(graph.num_vertices())

    for entity in entity_lists:
        attributes = entity.get_info()
        vertex = graph.vertex(entity.id())
        entity_name[vertex] = "#" + str(entity.id()) + "=" + entity.is_a()
        # 设置实体颜色
        if entity.is_a("IfcRelationship"):
            entity_type[vertex] = "IfcRelationship"
            entity_color[vertex] = color_map["IfcRelationship"]
            # 添加关联关系
            for key, value in attributes.items():
                if isinstance(value, ifcopenshell.entity_instance):
                    # print("add edge to " + str(entity.id()) + " from " + str(value.id()))
                    edge = graph.add_edge(vertex, graph.vertex(value.id()))
                    # 设置边宽度
                    edge_width[edge] = 1
                elif isinstance(value, tuple):
                    for item in value:
                        if isinstance(item, ifcopenshell.entity_instance):
                            # print("add edge to " + str(entity.id()) + " from " + str(item.id()))
                            edge = graph.add_edge(vertex, graph.vertex(item.id()))
                            edge_width[edge] = 1
        elif entity.is_a("IfcProduct"):
            entity_type[vertex] = "IfcProduct"
            entity_color[vertex] = color_map["IfcProduct"]
        else:
            entity_type[vertex] = "Others"
            entity_color[vertex] = color_map["Others"]
    # 设置孤立点的颜色
    for v in graph.vertices():
        # print(v.out_degree())
        if graph.vp.color[v] == "":
            graph.vp.color[v] = "#FFFFFF"
    return graph


if __name__ == "__main__":
    draw_legend(color_map)

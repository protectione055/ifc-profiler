import graph_tool.all as gt
import ifcopenshell
import os
import re
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import numpy as np

# 设置中文字体
plt.rc("font", family="AR PL UKai CN")
# 用来正常显示负号
plt.rcParams["axes.unicode_minus"] = False


def create_result_dir(base_dir, exp_name):
    """
    在指定目录生成新的文件夹，文件夹按照“实验名+时间戳”命名

    Args:
        base_dir (str): 基础目录路径
        exp_name (str): 实验名称

    Returns:
        str: 生成的结果文件夹路径
    """
    result_dir = os.path.join(
        base_dir, exp_name + "-" + datetime.now().strftime("%Y%m%d-%H%M%S")
    )
    if not os.path.exists(result_dir):
        os.makedirs(result_dir)
    return result_dir


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
    pattern = """#\d+=(IFC[A-Z]+)\(.*\);"""
    match = re.findall(pattern, line)
    if match:
        return True
    else:
        return False


# 三元颜色组合
three_color = ["#ffae49", "#44b7c2", "#024b7a"]


# 输入color_dict生成legend
def draw_legend(color_dict, result_path):
    # 绘制图例
    plt.figure(figsize=(5, 5))
    plt.title("图例")
    for entity_type, color in color_dict.items():
        plt.plot([], [], color=color, label=entity_type, marker="o", markersize=10)
    plt.legend()
    plt.axis("off")
    plt.savefig(result_path)


# 不同类型的实体对应的颜色
color_map = {
    "IfcRelationship": three_color[0],
    "IfcProduct": three_color[1],
    "Others": three_color[2],
}


def ifc_to_property_graph(file):
    """
    将IFC转换为属性图，每个实例对应一个顶点，每个关联关系对应一条边。

    每个顶点具有以下属性：

    name: 实例的名称，格式为#id=type

    color: 实例的颜色

    type: 实例的类型

    Args:
        file (str): IFC文件路径

    Returns:
        graph (Graph): 属性图表示的IFC模型，注意图中可能有空的顶点，因为IFC实例序号不一定是连续的。
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

    for entity in entity_lists:
        attributes = entity.get_info()
        vertex = graph.vertex(entity.id())
        entity_name[vertex] = "#" + str(entity.id()) + "=" + entity.is_a()

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

        # 设置顶点属性
        if entity.is_a("IfcRelationship"):
            entity_type[vertex] = "IfcRelationship"
            entity_color[vertex] = color_map["IfcRelationship"]
        elif entity.is_a("IfcProduct"):
            entity_type[vertex] = "IfcProduct"
            entity_color[vertex] = color_map["IfcProduct"]
        else:
            entity_type[vertex] = "Others"
            entity_color[vertex] = color_map["Others"]

    # 过滤所有name属性为空的顶点，并返回新的图
    graph = gt.GraphView(graph, vfilt=lambda v: graph.vp.name[v] != "")
    return graph


# 获取中心度最高的k个点
def get_top_k_central_nodes(graph, k, metric):
    # 计算中心度
    centrality_map, _ = gt.betweenness(graph)

    # 获取所有节点的中心度
    centralities = [centrality_map[v] for v in graph.iter_vertices()]
    print(centralities)

    # 找到中心度最大的k个点
    top_k_nodes = np.argsort(centralities)[-k:]

    return top_k_nodes


# 绘制直方图
def draw_hist(hist, title, x_lable, y_label,result_path, fig_size = (10, 5)):
    # 绘制度分布直方图
    plt.figure(figsize=fig_size)
    plt.title(title)
    plt.xlabel(x_lable)
    plt.ylabel(y_label)
    plt.bar([x[0] for x in hist], [x[1] for x in hist])
    plt.savefig(result_path)

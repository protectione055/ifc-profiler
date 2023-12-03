"""
这个程序用来分析IFC文件的中心性
"""
import os
import ifc_profile_util as util
import graph_tool as gt
import matplotlib.pyplot as plt

# 设置输入路径
dataset = "./bim_models_dataset/Duplex Apartment"
result = util.create_result_dir("./result", "ifc_centrality")


# 任务函数
def analyse_degree_centrality(graph):
    """
    获取所有点的中心度，按照中心度排序，输出到文件
    """
    hist = gt.stats.vertex_hist(graph, "total")

    print(util.get_top_k_central_nodes(graph, 10))


def analyse_betweenness_centrality(graph):
    pass


def analyse_closeness_centrality(graph):
    pass


"""
计算IFC图的度分布，拟合幂律分布，计算拟合优度
"""


def analyse_power_law(graph, filename):
    # 计算顶点的度，顶点按照度从大到小排序
    degrees = graph.degree_property_map("total").a
    sorted_vertices = sorted(
        graph.vertices(), key=lambda v: degrees[int(v)], reverse=True
    )
    labels = [graph.vp.name[v] for v in sorted_vertices]
    degrees_sorted = [degrees[int(v)] for v in sorted_vertices]

    # 将labels和degrees_sorted写入csv
    with open(os.path.join(result, f"degree_dist-{filename}.csv"), "w") as f:
        f.write("label,degree\n")
        for label, degree in zip(labels, degrees_sorted):
            f.write(f"{label},{degree}\n")

    # 绘制前截断100以后的实例
    if len(sorted_vertices) > 100:
        labels = [graph.vp.name[v] for v in sorted_vertices[:100]]
        degrees_sorted = [degrees[int(v)] for v in sorted_vertices[:100]]

    # 绘制直方图
    plt.rcParams["font.family"] = "Times New Roman"
    plt.figure(figsize=(20, 6), dpi=300)
    plt.bar(labels, degrees_sorted, width=0.8)
    plt.xlabel("IFC Instance")
    plt.ylabel("Degree")
    plt.title(f"Degree Distribution of {filename}")
    plt.xticks(rotation=45, fontsize="small", ha="right")
    plt.tight_layout()
    plt.savefig(os.path.join(result, f"degree_dist_hist-{filename}.png"))


# 任务列表
tasks = [
    analyse_power_law,
]


# 主程序
if __name__ == "__main__":
    for ifc_file in util.iterate_ifc_directory(dataset):
        print(f"{os.path.basename(__file__)}: {ifc_file}")
        ifc_graph = util.ifc_to_property_graph(ifc_file)

        for task in tasks:
            print(f"Running task {task.__name__}...")
            task(ifc_graph, os.path.basename(ifc_file))

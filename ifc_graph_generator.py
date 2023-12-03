from ifc_profile_util import *
import graph_tool.all as gt
import os

if __name__ == "__main__":
    dir = "./bim_models_dataset/mini-test"
    result_dir = create_result_dir("./result", "ifc_graph")

    draw_legend(color_map, os.path.join(result_dir, "legend.png"))

    for file in iterate_ifc_directory(dir):
        print(f"processing {file}")
        graph = ifc_to_property_graph(file)

        print("total vertices: ", graph.num_vertices())
        print("total edges: ", graph.num_edges())

        # 只生成有实体关系关联的顶点子图
        subgraph = gt.GraphView(
            graph, vfilt=lambda v: v.out_degree() > 0 or v.in_degree() > 0
        )
        # 为子图创建属性，不然会触发奇怪的numpy传播bug
        subgraph_color = subgraph.new_vp("string")
        subgraph.vp.color = subgraph_color
        subgraph_name = subgraph.new_vp("string")
        subgraph.vp.name = subgraph_name
        for v in subgraph.vertices():
            subgraph_color[v] = graph.vp.color[v]
            subgraph_name[v] = graph.vp.name[v]
        print(f"generatin relation subgraph with edges: {subgraph.num_vertices()}")
        pos = gt.fruchterman_reingold_layout(subgraph)
        gt.graph_draw(
            subgraph,
            pos=pos,
            vertex_text=subgraph.vp.name,
            vertex_text_position=0,
            vertex_text_size=12,
            vertex_text_color="#000000",
            vertex_size=12,
            output_size=(1000, 1000),
            bg_color="#ffffff",
            fit_view=True,
            vertex_fill_color=graph.vp.color,
            output=os.path.join(result_dir, file.split("/")[-1] + ".er.png"),
        )

        # 生成构件之间的关联关系图
        tmp = gt.GraphView(
            graph,
            vfilt=lambda v: graph.vp.type[v] != "Others"
            and graph.vp.type[v] != ""
            and (v.out_degree() > 0 or v.in_degree() > 0),
        )
        subgraph = gt.GraphView(
            tmp,
            vfilt=lambda v: graph.vp.type[v] != "IfcRelationship" or v.out_degree() > 1,
        )
        # 为子图创建属性，不然会触发奇怪的numpy传播bug
        subgraph_color = subgraph.new_vp("string")
        subgraph.vp.color = subgraph_color
        subgraph_name = subgraph.new_vp("string")
        subgraph.vp.name = subgraph_name
        for v in subgraph.vertices():
            subgraph_color[v] = graph.vp.color[v]
            subgraph_name[v] = graph.vp.name[v]
        print(f"generatin product subgraph with edges: {subgraph.num_vertices()}")
        print("reslt dir: ", result_dir)
        gt.graph_draw(
            subgraph,
            vertex_text=subgraph.vp.name,
            vertex_text_position=0,
            vertex_text_size=12,
            vertex_text_color="#000000",
            vertex_size=12,
            output_size=(1500, 1500),
            fit_view=True,
            bg_color="#ffffff",
            vertex_fill_color=graph.vp.color,
            output=os.path.join(result_dir, file.split("/")[-1] + ".product.png"),
        )

        # SBM
        # state = gt.minimize_blockmodel_dl(subgraph)
        # print("state entropy: ", state.entropy())
        # state.draw(
        #     output=os.path.join(result_dir, file.split("/")[-1] + ".sbm.png"),
        # )

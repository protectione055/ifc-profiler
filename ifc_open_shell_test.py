import ifcopenshell
import ifcopenshell.util.attribute
from ifc_profile_util import *

if __name__ == "__main__":
    file_path = "/home/zzm/projects/ifc-profiler/bim_models_dataset/真实数据集/华润总部春笋IFC数据集/HRARHIFC/SZW_WXH_ARCH_B4.ifc"
    graph = ifc_to_property_graph(file_path)
    graph_draw(
        graph,
        vertex_text=g.vertex_index,
        vertex_font_size=18,
        output_size=(200, 200),
        output="SZW_WXH_ARCH_B4-ifc.png",
    )

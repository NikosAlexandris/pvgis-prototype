from base64 import b64encode
from contextlib import suppress
from diagrams import Diagram, Cluster, Edge
from diagrams.custom import Custom

icons_path = "docs/icons"
logos_path = "docs/logos"
data_array_icon = f"{logos_path}/data_array.svg"


try:
    with suppress(FileNotFoundError):
        graph_attr = {"splines":"spline"}
        with Diagram("Chunked Data",
            show=False,
            filename="chunked_data",
            direction="TB",
            graph_attr=graph_attr,
        ) as diagram:
            with Cluster("Solar Irradiance", direction="TB"):

                with Cluster("Global Solar Irradiance"):
                    row_1 = [Custom(f"{idx}", data_array_icon) for idx in range(1, 4)]
                    row_2 = [Custom(f"{idx}",
                                    data_array_icon) for idx in range(4, 7)]
                    row_3 = [Custom(f"{idx}",
                                    data_array_icon) for idx in range(7, 10)]
                    row_1[0] - Edge(style='invis') - row_1[1] - Edge(style='invis') - row_1[2]
                    row_2[0] - Edge(style='invis') - row_2[1] - Edge(style='invis') - row_2[2]
                    row_3[0] - Edge(style='invis') - row_3[1] - Edge(style='invis') - row_3[2]
                
                with Cluster("Direct Solar Irradiance"):
                    row_1 = [Custom(f"{idx}", data_array_icon) for idx in range(1, 4)]
                    row_2 = [Custom(f"{idx}",
                                    data_array_icon) for idx in range(4, 7)]
                    row_3 = [Custom(f"{idx}",
                                    data_array_icon) for idx in range(7, 10)]
                    row_1[0] - Edge(style='invis') - row_1[1] - Edge(style='invis') - row_1[2]
                    row_2[0] - Edge(style='invis') - row_2[1] - Edge(style='invis') - row_2[2]
                    row_3[0] - Edge(style='invis') - row_3[1] - Edge(style='invis') - row_3[2]
            
            with Cluster("Meteorological variables", direction="TB"):

                with Cluster("Temperature"):
                    row_1 = [Custom(f"{idx}", data_array_icon) for idx in range(1, 4)]
                    row_2 = [Custom(f"{idx}",
                                    data_array_icon) for idx in range(4, 7)]
                    row_3 = [Custom(f"{idx}",
                                    data_array_icon) for idx in range(7, 10)]
                    row_1[0] - Edge(style='invis') - row_1[1] - Edge(style='invis') - row_1[2]
                    row_2[0] - Edge(style='invis') - row_2[1] - Edge(style='invis') - row_2[2]
                    row_3[0] - Edge(style='invis') - row_3[1] - Edge(style='invis') - row_3[2]

                with Cluster("Wind Speed"):
                    row_1 = [Custom(f"{idx}", data_array_icon) for idx in range(1, 4)]
                    row_2 = [Custom(f"{idx}",
                                    data_array_icon) for idx in range(4, 7)]
                    row_3 = [Custom(f"{idx}",
                                    data_array_icon) for idx in range(7, 10)]
                    row_1[0] - Edge(style='invis') - row_1[1] - Edge(style='invis') - row_1[2]
                    row_2[0] - Edge(style='invis') - row_2[1] - Edge(style='invis') - row_2[2]
                    row_3[0] - Edge(style='invis') - row_3[1] - Edge(style='invis') - row_3[2]

            with Cluster("Spectral Factor"):
                row_1 = [Custom(f"{idx}", data_array_icon) for idx in range(1, 4)]
                row_2 = [Custom(f"{idx}",
                                data_array_icon) for idx in range(4, 7)]
                row_3 = [Custom(f"{idx}",
                                data_array_icon) for idx in range(7, 10)]
                row_1[0] - Edge(style='invis') - row_1[1] - Edge(style='invis') - row_1[2]
                row_2[0] - Edge(style='invis') - row_2[1] - Edge(style='invis') - row_2[2]
                row_3[0] - Edge(style='invis') - row_3[1] - Edge(style='invis') - row_3[2]

            # Encode diagram as a PNG and print it in HTML Image format

            png = b64encode(diagram.dot.pipe(format="png")).decode()

    # Finally, print

    print(f'<img src="data:image/png;base64, {png}"/>')

except Exception as e:
    print(f"An error occurred: {e}")
    import traceback
    traceback.print_exc()  # This prints the full traceback

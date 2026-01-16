import matplotlib.pyplot as plt
import networkx as nx

def draw(model, pos):
    plt.clf()

    nx.draw(
        model.graph,
        pos=pos,
        node_size=10,
        edge_color="lightgray",
        with_labels=False
    )

    for agent in model.agents:
        x, y = pos[agent.pos]

        plt.scatter(x, y, s=100, c="red", zorder=3)
        
        plt.text(
                x,
                y,
                str(agent.unique_id),
                fontsize=9,
                color="black",
                ha="center",
                va="center",
                zorder=4
            )


    plt.gca().invert_yaxis()
    plt.pause(0.1)
import matplotlib.pyplot as plt
import networkx as nx

interpolate_agents_position = True

def interpolate_position(agent, pos, model):
    if (agent.remaining_time <= 0 or agent.previous_node is None or agent.target is None):
        return pos[agent.pos]   

    u = agent.previous_node
    v = agent.target

    total_time = model.graph.edges[u, v]["distance"]
    progress = 1 - agent.remaining_time / total_time

    x_u, y_u = pos[u]
    x_v, y_v = pos[v]

    x = x_u + progress * (x_v - x_u)
    y = y_u + progress * (y_v - y_u)

    return x, y

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
        x, y = interpolate_position(agent, pos, model) if interpolate_agents_position else pos[agent.pos]

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
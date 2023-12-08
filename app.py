from flask import Flask, render_template, request
import json
import heapq
import networkx as nx
import matplotlib
matplotlib.use('Agg')  # Gunakan backend Agg secara eksplisit
import matplotlib.pyplot as plt

app = Flask(__name__)

# Muat data dari file JSON
with open('data_rute.json', 'r') as file:
    data = json.load(file)

destinations = data['destinations']
matrix = data['matrix']

def branch_and_bound(matrix, start, end):
    n = len(matrix)
    visited = [False] * n
    path = [start]
    cost = 0

    priority_queue = [(0, start, visited, path, cost)]

    while priority_queue:
        _, current, visited, path, cost = heapq.heappop(priority_queue)

        if current == end:
            return path, cost

        for neighbor in range(n):
            if not visited[neighbor] and matrix[current][neighbor] != float('inf'):
                new_visited = visited[:]
                new_visited[neighbor] = True
                new_path = path + [neighbor]
                new_cost = cost + matrix[current][neighbor]

                heapq.heappush(priority_queue, (new_cost, neighbor, new_visited, new_path, new_cost))

    return None, float('inf')

def plot_route(start, end, path, plot_filename):
    G = nx.Graph()

    # Tambahkan edge untuk rute tercepat
    route_edges = [(destinations[path[i]], destinations[path[i + 1]]) for i in range(len(path) - 1)]
    for edge in route_edges:
        weight = matrix[destinations.index(edge[0])][destinations.index(edge[1])]
        G.add_edge(edge[0], edge[1], weight=weight)

    pos = nx.spring_layout(G)  # Set node positions with a spring layout

    node_colors = ['orange' if node == start else 'green' if node == end else 'skyblue' for node in G.nodes]

    # Draw nodes
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=700)

    # Draw edges
    edge_labels = {(edge[0], edge[1]): G.get_edge_data(edge[0], edge[1])['weight'] for edge in G.edges}
    nx.draw_networkx_edges(G, pos, edgelist=route_edges, width=2, edge_color='red')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red')

    # Draw labels for nodes
    nx.draw_networkx_labels(G, pos, font_size=8)

    plt.title(f"Rute Tercepat dari {start} ke {end}")

    # Simpan graf sebagai file gambar dengan nama yang sesuai
    plot_path = f"static/{plot_filename}.png"
    plt.savefig(plot_path, format="png")
    plt.close()  # Tutup plot untuk mencegah ditampilkan di aplikasi web

    return plot_path


def draw_and_save_graph():
    G = nx.Graph()

    # Tambahkan edge berdasarkan data JSON
    for edge in data["edges"]:
        G.add_edge(edge[0], edge[1], weight=matrix[destinations.index(edge[0])][destinations.index(edge[1])])

    pos = {
        "Pos Utama IT Del": (-2, 0),
        "Asrama Pniel": (-1, 1.8),
        "Jl. PI Del": (-1, 0),
        "Auditorium": (-0.5, -1),
        "Perpustakaan IT Del": (0.2, -2),
        "Plaza": (1.8, -1),
        "KB": (2, -2),
        "Gd 5": (0.8, 0.5),
        "Gd 7": (1, 2.3),
        "Gd 8": (4, -3),
        "Asrama Kembar": (4, -4),
        "Pos 4": (2, -5),
        "OT": (4, 0)
    }

    # Tambahkan semua destinasi sebagai node
    for destination in destinations:
        G.add_node(destination)

    # Draw nodes
    nx.draw_networkx_nodes(G, pos, node_size=700)

    # Draw edges
    edge_labels = {(edge[0], edge[1]): G.get_edge_data(edge[0], edge[1])['weight'] for edge in G.edges}
    nx.draw_networkx_edges(G, pos, width=2)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red')

    # Draw labels for nodes
    nx.draw_networkx_labels(G, pos, font_size=8)

    plt.title("Graf dengan Semua Lokasi, Posisi Disesuaikan, dan Edge yang Sesuai")

    # Simpan graf sebagai file gambar dengan nama yang sesuai
    plot_path = "static/dynamic_graph.png"
    plt.savefig(plot_path, format="png")
    plt.close()

    return plot_path


# Ubah rute untuk menerima input dari pengguna
@app.route('/', methods=['GET', 'POST'])
def shortest_path_web():
    start_point = "Pos Utama IT Del"
    end_point = "OT"
    final_route = None

    if request.method == 'POST':
        # Dapatkan start_point dan end_point dari pengiriman formulir
        start_point = request.form['start_point']
        end_point = request.form['end_point']

        # Temukan rute terpendek untuk start_point dan end_point yang diberikan
        path, total_cost = branch_and_bound(matrix, destinations.index(start_point), destinations.index(end_point))

        if path:
            total_destinations_visited = len(path)
            total_distance = total_cost

            plot_filename = "gambar_graph"
            plot_path = plot_route(start_point, end_point, path, plot_filename)

            # Gambar dan simpan graf secara dinamis
            dynamic_plot_path = draw_and_save_graph()

            # Modifikasi final_route untuk hanya mencakup informasi yang diperlukan
            final_route = {
                "path": [destinations[i] for i in path],
                "total_destinations_visited": total_destinations_visited,
                "total_distance": total_distance,
                "plot_path": plot_path,
                "dynamic_plot_path": dynamic_plot_path
            }

    return render_template('optimasirute.html', final_route=final_route, start_point=start_point, end_point=end_point, destinations=destinations)

if __name__ == '__main__':
    app.run(debug=True)
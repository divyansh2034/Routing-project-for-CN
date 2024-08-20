import tkinter as tk
from tkinter import messagebox
import heapq
import math
import re

class RouterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Router Network Simulator")
        self.scrollbar = tk.Scrollbar(root, orient="vertical")
        self.canvas = tk.Canvas(root, yscrollcommand=self.scrollbar.set)
        self.content_frame = tk.Frame(self.canvas, bg="#f0f0f0")
        self.canvas.create_window((0, 0), window=self.content_frame, anchor="nw")
        self.scrollbar.config(command=self.canvas.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.content_frame.bind("<Configure>", self.on_frame_configure)
        self.history = []
        self.router_ips = []
        self.network_counts = []
        self.network_ips = []
        self.congestion = []
        self.weights = []
        self.show_matrix_input()

    def on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def show_matrix_input(self):
        self.clear_widgets()
        tk.Label(self.content_frame, text="ENTER THE ROUTER CONNECTION (Adjacency Matrix):", font=("Helvetica", 14, "bold"), bg="#f0f0f0").pack(pady=10)
        self.router_count_var = tk.StringVar()
        tk.Entry(self.content_frame, textvariable=self.router_count_var, font=("Helvetica", 12)).pack(pady=5)
        self.submit_router_count_button = tk.Button(self.content_frame, text="Submit Router Count", command=self.submit_router_count, bg="black", fg="white", font=("Helvetica", 12, "bold"))
        self.submit_router_count_button.pack(pady=10)

        if self.history:
            self.back_button = tk.Button(self.content_frame, text="Back", command=self.go_back, bg="black", fg="white", font=("Helvetica", 12, "bold"))
            self.back_button.pack(pady=10)

    def submit_router_count(self):
        try:
            self.k = int(self.router_count_var.get())
            if self.k <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Input Error", "Please enter a valid positive integer for the number of routers.")
            return

        self.matrix_entries = [[tk.StringVar() for _ in range(self.k)] for _ in range(self.k)]
        for i in range(self.k):
            row_frame = tk.Frame(self.content_frame, bg="#f0f0f0")
            row_frame.pack(pady=5)
            for j in range(self.k):
                tk.Entry(row_frame, textvariable=self.matrix_entries[i][j], width=5, font=("Helvetica", 12)).grid(row=0, column=j, padx=5)

        self.submit_matrix_button = tk.Button(self.content_frame, text="Submit Matrix", command=self.submit_matrix, bg="black", fg="white", font=("Helvetica", 12, "bold"))
        self.submit_matrix_button.pack(pady=10)

        if self.history:
            self.back_button = tk.Button(self.content_frame, text="Back", command=self.go_back, bg="black", fg="white", font=("Helvetica", 12, "bold"))
            self.back_button.pack(pady=10)

    def submit_matrix(self):
        try:
            self.n = [[int(self.matrix_entries[i][j].get()) for j in range(self.k)] for i in range(self.k)]
        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid integers for the matrix.")
            return

        self.history.append(self.show_matrix_input)
        self.show_weights_input()

    def show_weights_input(self):
        self.clear_widgets()
        tk.Label(self.content_frame, text="Enter weights for each connection (0 for no connection):", font=("Helvetica", 14, "bold"), bg="#f0f0f0").pack(pady=10)

        self.weight_entries = [[tk.StringVar() for _ in range(self.k)] for _ in range(self.k)]
        for i in range(self.k):
            row_frame = tk.Frame(self.content_frame, bg="#f0f0f0")
            row_frame.pack(pady=5)
            for j in range(self.k):
                tk.Entry(row_frame, textvariable=self.weight_entries[i][j], width=5, font=("Helvetica", 12)).grid(row=0, column=j, padx=5)

        self.submit_weights_button = tk.Button(self.content_frame, text="Submit Weights", command=self.submit_weights, bg="black", fg="white", font=("Helvetica", 12, "bold"))
        self.submit_weights_button.pack(pady=10)

        if self.history:
            self.back_button = tk.Button(self.content_frame, text="Back", command=self.go_back, bg="black", fg="white", font=("Helvetica", 12, "bold"))
            self.back_button.pack(pady=10)

    def submit_weights(self):
        try:
            self.weights = [[int(self.weight_entries[i][j].get()) for j in range(self.k)] for i in range(self.k)]
        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid integers for the weights.")
            return

        self.history.append(self.show_weights_input)
        self.show_matrix_and_network()

    def show_matrix_and_network(self):
        self.clear_widgets()
        matrix_str = "\n".join(["\t".join(map(str, row)) for row in self.n])
        tk.Label(self.content_frame, text=f"Adjacency Matrix:\n{matrix_str}", font=("Helvetica", 12), bg="#f0f0f0").pack(pady=10)

        self.draw_router_network()

        tk.Label(self.content_frame, text="Enter the number of networks for each router:", font=("Helvetica", 14, "bold"), bg="#f0f0f0").pack(pady=10)

        self.network_counts = []
        self.network_entries = []

        for i in range(self.k):
            tk.Label(self.content_frame, text=f"Router {i+1} Networks:", font=("Helvetica", 12), bg="#f0f0f0").pack(pady=5)
            network_var = tk.StringVar()
            tk.Entry(self.content_frame, textvariable=network_var, font=("Helvetica", 12)).pack(pady=5)
            self.network_entries.append(network_var)

        self.submit_network_button = tk.Button(self.content_frame, text="Submit", command=self.submit_network_counts, bg="black", fg="white", font=("Helvetica", 12, "bold"))
        self.submit_network_button.pack(pady=10)

        if self.history:
            self.back_button = tk.Button(self.content_frame, text="Back", command=self.go_back, bg="black", fg="white", font=("Helvetica", 12, "bold"))
            self.back_button.pack(pady=10)

    def draw_router_network(self):
        canvas_frame = tk.Frame(self.content_frame, bg="#f0f0f0")
        canvas_frame.pack(pady=10)

        canvas = tk.Canvas(canvas_frame, width=500, height=500, bg="white")
        canvas.pack()

        radius = 20
        center = (250, 250)
        angle_step = 360 / self.k

        nodes = []
        for i in range(self.k):
            angle = i * angle_step
            x = center[0] + 150 * math.cos(math.radians(angle))
            y = center[1] + 150 * math.sin(math.radians(angle))
            nodes.append((x, y))
            canvas.create_oval(x - radius, y - radius, x + radius, y + radius, fill="lightblue", outline="black")
            canvas.create_text(x, y, text=f"Router {i+1}", font=("Helvetica", 10))

        for i in range(self.k):
            for j in range(i + 1, self.k):
                if self.n[i][j] > 0:
                    canvas.create_line(nodes[i][0], nodes[i][1], nodes[j][0], nodes[j][1], fill="black")

    def submit_network_counts(self):
        try:
            self.network_counts = [int(var.get()) for var in self.network_entries]
            if any(count <= 0 for count in self.network_counts):
                raise ValueError
        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid positive integers for all network counts.")
            return

        self.history.append(self.show_matrix_and_network)
        self.show_router_ip_input()

    def show_router_ip_input(self):
        self.clear_widgets()
        total_networks = sum(self.network_counts)
        tk.Label(self.content_frame, text="Enter IP addresses for each network:", font=("Helvetica", 14, "bold"), bg="#f0f0f0").pack(pady=10)

        self.network_ip_entries = [tk.StringVar() for _ in range(total_networks)]
        self.network_ip_labels = []

        for i in range(total_networks):
            tk.Label(self.content_frame, text=f"Network {i+1} IP:", font=("Helvetica", 12), bg="#f0f0f0").pack(pady=5)
            tk.Entry(self.content_frame, textvariable=self.network_ip_entries[i], font=("Helvetica", 12)).pack(pady=5)

        self.submit_ips_button = tk.Button(self.content_frame, text="Submit IPs", command=self.submit_ips, bg="black", fg="white", font=("Helvetica", 12, "bold"))
        self.submit_ips_button.pack(pady=10)

        if self.history:
            self.back_button = tk.Button(self.content_frame, text="Back", command=self.go_back, bg="black", fg="white", font=("Helvetica", 12, "bold"))
            self.back_button.pack(pady=10)

    def submit_ips(self):
        try:
            self.network_ips = [var.get() for var in self.network_ip_entries]
            if len(set(self.network_ips)) != len(self.network_ips):
                raise ValueError
        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid and unique IP addresses.")
            return

        self.router_ips = self.network_ips[:]
        self.history.append(self.show_router_ip_input)
        self.show_congestion_input()

    def show_congestion_input(self):
        self.clear_widgets()
        tk.Label(self.content_frame, text="Dynamic Routing - Enter Congestion for Routers:", font=("Helvetica", 14, "bold"), bg="#f0f0f0").pack(pady=10)

        self.congestion_vars = []
        for i in range(self.k):
            tk.Label(self.content_frame, text=f"Router {i+1} Congestion (0=no, 1=yes):", font=("Helvetica", 12), bg="#f0f0f0").pack(pady=5)
            congestion_var = tk.StringVar()
            tk.Entry(self.content_frame, textvariable=congestion_var, font=("Helvetica", 12)).pack(pady=5)
            self.congestion_vars.append(congestion_var)

        self.submit_congestion_button = tk.Button(self.content_frame, text="Submit Congestion Data", command=self.submit_congestion_data, bg="black", fg="white", font=("Helvetica", 12, "bold"))
        self.submit_congestion_button.pack(pady=10)

        if self.history:
            self.back_button = tk.Button(self.content_frame, text="Back", command=self.go_back, bg="black", fg="white", font=("Helvetica", 12, "bold"))
            self.back_button.pack(pady=10)

    def submit_congestion_data(self):
        try:
            self.congestion = [int(var.get()) for var in self.congestion_vars]
            if any(c not in (0, 1) for c in self.congestion):
                raise ValueError
        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid congestion data (0 or 1).")
            return

        self.show_routing_type_selection()

    def show_routing_type_selection(self):
        self.clear_widgets()
        tk.Label(self.content_frame, text="Select Routing Type:", font=("Helvetica", 14, "bold"), bg="#f0f0f0").pack(pady=10)

        tk.Button(self.content_frame, text="Static Routing", command=lambda: self.show_source_destination("Static Routing"), bg="black", fg="white", font=("Helvetica", 12, "bold")).pack(pady=5)
        tk.Button(self.content_frame, text="Dynamic Routing", command=lambda: self.show_source_destination("Dynamic Routing"), bg="black", fg="white", font=("Helvetica", 12, "bold")).pack(pady=5)

        if self.history:
            self.back_button = tk.Button(self.content_frame, text="Back", command=self.go_back, bg="black", fg="white", font=("Helvetica", 12, "bold"))
            self.back_button.pack(pady=10)

    def show_source_destination(self, routing_type):
        self.clear_widgets()
        tk.Label(self.content_frame, text=f"{routing_type} - Enter Source and Destination IPs:", font=("Helvetica", 14, "bold"), bg="#f0f0f0").pack(pady=10)

        self.source_ip_var = tk.StringVar()
        self.destination_ip_var = tk.StringVar()

        tk.Label(self.content_frame, text="Source IP:", font=("Helvetica", 12), bg="#f0f0f0").pack(pady=5)
        tk.Entry(self.content_frame, textvariable=self.source_ip_var, font=("Helvetica", 12)).pack(pady=5)

        tk.Label(self.content_frame, text="Destination IP:", font=("Helvetica", 12), bg="#f0f0f0").pack(pady=5)
        tk.Entry(self.content_frame, textvariable=self.destination_ip_var, font=("Helvetica", 12)).pack(pady=5)

        tk.Button(self.content_frame, text="Submit", command=lambda: self.calculate_shortest_path(routing_type), bg="black", fg="white", font=("Helvetica", 12, "bold")).pack(pady=10)

        if self.history:
            self.back_button = tk.Button(self.content_frame, text="Back", command=self.go_back, bg="black", fg="white", font=("Helvetica", 12, "bold"))
            self.back_button.pack(pady=10)

    def calculate_shortest_path(self, routing_type):
        source_ip = self.source_ip_var.get()
        destination_ip = self.destination_ip_var.get()

        if not is_valid_ip(source_ip) or not is_valid_ip(destination_ip):
            messagebox.showerror("Input Error", "Please enter valid IP addresses.")
            return

        if source_ip not in self.router_ips or destination_ip not in self.router_ips:
            messagebox.showerror("Input Error", "Source or destination IP not found in router IPs.")
            return

        source_index = self.router_ips.index(source_ip)
        destination_index = self.router_ips.index(destination_ip)

        if routing_type == "Static Routing":
            path, distance = self.dijkstra(source_index, destination_index)
        elif routing_type == "Dynamic Routing":
            if self.congestion[source_index] == 1 or self.congestion[destination_index] == 1:
                messagebox.showinfo("Result", "Path cannot be found as the source or destination router is congested.")
                return
            path, distance = self.dijkstra_with_congestion(source_index, destination_index, self.congestion)

        if path:
            path_ips = [self.router_ips[i] for i in path]
            path_str = " -> ".join(path_ips)
            messagebox.showinfo("Result", f"Shortest Path: {path_str}\nTotal Distance: {distance}")
        else:
            messagebox.showinfo("Result", "No path found.")

    def dijkstra(self, start, end):
        distances = [float('inf')] * self.k
        distances[start] = 0
        pq = [(0, start)]
        previous_nodes = [None] * self.k

        while pq:
            current_distance, current_node = heapq.heappop(pq)

            if current_node == end:
                break

            for neighbor in range(self.k):
                if self.n[current_node][neighbor] > 0:
                    distance = self.weights[current_node][neighbor]
                    new_distance = current_distance + distance

                    if new_distance < distances[neighbor]:
                        distances[neighbor] = new_distance
                        previous_nodes[neighbor] = current_node
                        heapq.heappush(pq, (new_distance, neighbor))

        path = []
        if distances[end] < float('inf'):
            while end is not None:
                path.insert(0, end)
                end = previous_nodes[end]
        return path, distances[path[-1]] if path else float('inf')

    def dijkstra_with_congestion(self, start, end, congestion):
        distances = [float('inf')] * self.k
        distances[start] = 0
        pq = [(0, start)]
        previous_nodes = [None] * self.k

        while pq:
            current_distance, current_node = heapq.heappop(pq)

            if current_node == end:
                break

            for neighbor in range(self.k):
                if self.n[current_node][neighbor] > 0:
                    if congestion[neighbor] == 1:
                        continue  # Skip congested routers
                    distance = self.weights[current_node][neighbor]
                    new_distance = current_distance + distance

                    if new_distance < distances[neighbor]:
                        distances[neighbor] = new_distance
                        previous_nodes[neighbor] = current_node
                        heapq.heappush(pq, (new_distance, neighbor))

        path = []
        if distances[end] < float('inf'):
            while end is not None:
                path.insert(0, end)
                end = previous_nodes[end]
        return path, distances[path[-1]] if path else float('inf')

    def clear_widgets(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def go_back(self):
        if self.history:
            self.clear_widgets()
            self.history.pop()()
        else:
            self.root.quit()

def is_valid_ip(ip):
    pattern = re.compile(r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$")
    return bool(pattern.match(ip))

if __name__ == "__main__":
    root = tk.Tk()
    app = RouterApp(root)
    root.mainloop()

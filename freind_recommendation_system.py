from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/recommend', methods=['POST'])
def recommend():
    try:
        # Parse input data
        num_edges = int(request.form.get('num_edges', 0))
        edges = request.form.getlist('edges[]')  # Adjust to match frontend data format
        num_recommendations = int(request.form.get('num_recommendations', 0))

        # Create the graph
        import networkx as nx
        G = nx.Graph()

        for edge in edges:
            if edge:
                u, v = map(int, edge.split())
                G.add_edge(u, v)

        # Recommendation logic
        def recommend_friends(graph, search_node, num_recommendations):
            from collections import Counter

            if search_node not in graph:
                return []

            friends = set(graph.neighbors(search_node))
            recommendations = []
            for friend in friends:
                recommendations.extend(graph.neighbors(friend))
            recommendations = [node for node in recommendations if node not in friends and node != search_node]

            recommendation_counts = Counter(recommendations)
            shortest_paths = {}
            for rec in set(recommendations):
                try:
                    shortest_paths[rec] = nx.shortest_path_length(graph, source=search_node, target=rec)
                except nx.NetworkXNoPath:
                    continue

            sorted_recommendations = sorted(
                shortest_paths.items(),
                key=lambda x: (x[1], -recommendation_counts[x[0]])
            )
            return [rec for rec, _ in sorted_recommendations[:num_recommendations]]

        # Get recommendations for all nodes
        recommendations = {}
        for node in G.nodes():
            recommendations[node] = recommend_friends(G, node, num_recommendations)

        return jsonify(recommendations)
    
    except Exception as e:
        # Log the error for debugging
        return jsonify({'error': str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)

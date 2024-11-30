from flask import Flask, request, jsonify
from flask_cors import CORS
import networkx as nx
from collections import Counter

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
        G = nx.Graph()

        for edge in edges:
            if edge:
                u, v = map(int, edge.split())
                G.add_edge(u, v)

        # Recommendation logic
        def recommend_friends(graph, search_node, num_recommendations):
            if search_node not in graph:
                return []

            # Get direct friends of the search node
            friends = set(graph.neighbors(search_node))

            # Collect potential recommendations
            recommendations = []
            for friend in friends:
                recommendations.extend(graph.neighbors(friend))

            # Filter out nodes that are already direct friends or the search node itself
            recommendations = [
                node for node in recommendations
                if node not in friends and node != search_node
            ]

            # Count occurrences of potential recommendations
            
            recommendation_counts = Counter(recommendations)
        # shees's part start
            shortest_paths = {} #{4 , 2}
            for rec in set(recommendations): # rec == recommended node (6, 3)
                try: #shothest_path stores in diction like (recommended node, total weight)
                    shortest_paths[rec] = nx.shortest_path_length(graph, source=search_node, target=rec)
                except nx.NetworkXNoPath:
                    continue
            #sort with the priority
            sorted_recommendations = sorted(
                shortest_paths.items(),
                #it sort with shortest parh if the path is same then it get the prority of occurence
                key=lambda x: (x[1], -recommendation_counts[x[0]])
            )
            #return will give the number of recommendations want
            return [rec for rec, _ in sorted_recommendations[:num_recommendations]]
        #shees's part end

            # Return top recommendations based on frequency
            # return [rec for rec, _ in recommendation_counts.most_common(num_recommendations)]

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

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.nn import GCNConv

class RoadRiskGNN(nn.Module):
    """
    Graph Convolutional Network that predicts edge risk factors
    from node structural and environmental features.
    """
    def __init__(self, in_channels: int = 4, hidden_channels: int = 16, out_channels: int = 4):
        super(RoadRiskGNN, self).__init__()
        self.conv1 = GCNConv(in_channels, hidden_channels)
        self.conv2 = GCNConv(hidden_channels, out_channels)
        self.edge_predictor = nn.Sequential(
            nn.Linear(out_channels * 2 + 1, 8),
            nn.ReLU(),
            nn.Linear(8, 1),
            nn.Sigmoid()
        )

    def forward(self, x, edge_index, edge_attr):
        # x: Node features [num_nodes, in_channels]
        # edge_index: Graph connectivity [2, num_edges]
        # edge_attr: Edge features [num_edges, 1] (base_weight)
        h = self.conv1(x, edge_index)
        h = F.relu(h)
        h = self.conv2(h, edge_index)
        
        # Predict risk for each edge from source node, target node, and base attribute
        src, dst = edge_index[0], edge_index[1]
        edge_feat = torch.cat([h[src], h[dst], edge_attr], dim=-1)
        risk = self.edge_predictor(edge_feat)
        return risk

# Singleton model instance
_gnn_model = None

def get_gnn_model() -> RoadRiskGNN:
    global _gnn_model
    if _gnn_model is None:
        _gnn_model = RoadRiskGNN()
        _gnn_model.eval()
    return _gnn_model

def predict_edge_weights(
    node_features: dict[str, list[float]],
    edge_list: list[tuple[str, str, float]]
) -> dict[tuple[str, str], float]:
    """
    Runs PyTorch Geometric inference to adjust road weights based on GNN predicted risk.
    """
    if not node_features or not edge_list:
        return {}

    node_to_idx = {nid: i for i, nid in enumerate(node_features.keys())}
    x = torch.tensor(list(node_features.values()), dtype=torch.float)

    edges_src = []
    edges_dst = []
    edge_weights = []

    for u, v, w in edge_list:
        if u in node_to_idx and v in node_to_idx:
            edges_src.append(node_to_idx[u])
            edges_dst.append(node_to_idx[v])
            edge_weights.append([w])

    if not edges_src:
        return {}

    edge_index = torch.tensor([edges_src, edges_dst], dtype=torch.long)
    edge_attr = torch.tensor(edge_weights, dtype=torch.float)

    model = get_gnn_model()
    with torch.no_grad():
        risk_scores = model(x, edge_index, edge_attr)

    adjusted_weights = {}
    for i, (u, v, w) in enumerate(edge_list):
        if i < len(risk_scores):
            risk = float(risk_scores[i].item())
            # Edge weight penalty proportional to GNN predicted risk
            adjusted_weights[(u, v)] = round(w * (1.0 + risk * 0.75), 3)
        else:
            adjusted_weights[(u, v)] = w

    return adjusted_weights


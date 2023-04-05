'''RegGNN regression model architecture.

    torch_geometric needs to be installed.
    '''

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.nn.dense import DenseGCNConv

from torch_geometric.nn.conv import MessagePassing
from torch_geometric.utils import add_remaining_self_loops, to_dense_adj
from torch.nn import Linear as Lin
from torch_geometric.nn import SAGEConv

# pass messages between different genes in same cell
class FeatGraphConv(MessagePassing):
    def __init__(self, in_channels,hidden , out_channels, aggr='mean', bias = True,
                     **kwargs):
        super(FeatGraphConv, self).__init__(aggr=aggr, **kwargs)
        self.lin1 = Lin(2*hidden, out_channels, bias=bias)
        self.lin2 = Lin(in_channels, hidden, bias=bias)

    def forward(self, x, edge_index, edge_weight=None, size=None):
        # edge_index = add_remaining_self_loops(edge_index=edge_index.t())
        # edge_index = edge_index.t()
        # edge_index = to_dense_adj(edge_index)
        # print(x.dtype)
        # print(edge_index.dtype)
        h = self.lin2(x)
        edge_index = edge_index.int()
        edge_index = edge_index.nonzero().contiguous()
        edge_index = edge_index.t()
        return self.propagate(edge_index, size=size, x=x, h=h,
                              edge_weight=edge_weight)

    def message(self, h_j, edge_weight):
        return h_j if edge_weight is None else edge_weight.view(-1, 1) * h_j

    def update(self, aggr_out, h):
        return self.lin1(torch.cat((h, aggr_out), 1))

    def loss(self, pred, score):
        return F.mse_loss(pred, score)

# message passing and then fully connected layer to predict protein expression
class RegGNN(nn.Module):
    def __init__(self, in_channels):
        super(RegGNN, self).__init__()

        self.conv1 = FeatGraphConv(in_channels, in_channels, in_channels, aggr='mean')
        self.lin = Lin(110, 110)

    def forward(self, x, edge_index):
        x = torch.relu(self.conv1(x, edge_index))
        x = x.t()
        x = self.lin(x)
        x = x.t()
        return x

    def loss(self, pred, score):
        return F.mse_loss(pred, score)

# class RegGNN(nn.Module):
#     '''Regression using a DenseGCNConv layer from pytorch geometric.

#            Layers in this model are identical to GCNConv.
#     '''

#     def __init__(self, nfeat, nhid, nclass, dropout):
#         super(RegGNN, self).__init__()

#         self.gc1 = DenseGCNConv(nfeat, nhid)
#         self.gc2 = DenseGCNConv(nhid, nclass)
#         self.conv1 = SAGEConv(nfeat, 256)
#         self.conv2 = SAGEConv(256, 64)
#         self.lin = Lin(64, nfeat)
#         self.dropout = dropout
#         # self.LinearLayer = nn.Linear(nfeat, 1)
#         self.LinearLayer = Lin(nclass, 7476)

#         # def forward(self, x, edge_index):
#         #     x = F.relu(self.gc1(x, edge_index))

#         #     x = F.dropout(x, self.dropout, training=self.training)
#         #     x = self.gc2(x, edge_index)
#         #     # x = self.LinearLayer(torch.transpose(x, 2, 1))
#         #     x = self.LinearLayer(x)

#         #     # return torch.transpose(x, 2, 1)
#         #     return x

#     def forward(self, x, edge_index):
#         edge_index = edge_index.t()      
#         x = F.relu(self.conv1(x, edge_index))
#         x = F.dropout(x, self.dropout, training=self.training)
#         x = self.conv2(x, edge_index)
#         x = self.lin(x)
#         return x

#     def loss(self, pred, score):
#         return F.mse_loss(pred, score)

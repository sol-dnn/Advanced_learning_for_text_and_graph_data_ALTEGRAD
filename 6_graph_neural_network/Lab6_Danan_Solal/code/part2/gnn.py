"""
Deep Learning on Graphs - ALTEGRAD - Nov 2024
"""

import time
import networkx as nx
import numpy as np
import scipy.sparse as sp
from sklearn.model_selection import train_test_split
import torch
import torch.nn as nn
from torch import optim

from models import GNN
from utils import create_dataset, sparse_mx_to_torch_sparse_tensor

# Initializes device
device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")

# Hyperparameters
epochs = 200
batch_size = 8
n_hidden_1 = 16
n_hidden_2 = 32
n_hidden_3 = 32
learning_rate = 0.01

# Generates synthetic dataset
Gs, y = create_dataset()
n_class = np.unique(y).size

# Splits the dataset into a training and a test set
G_train, G_test, y_train, y_test = train_test_split(Gs, y, test_size=0.1)

N_train = len(G_train)
N_test = len(G_test)

# Initializes model and optimizer
model = GNN(1, n_hidden_1, n_hidden_2, n_hidden_3, n_class, device).to(device)
optimizer = optim.Adam(model.parameters(), lr=learning_rate)
loss_function = nn.CrossEntropyLoss()

# Trains the model
for epoch in range(epochs):
    t = time.time()
    model.train()
    
    train_loss = 0
    correct = 0
    count = 0
    for i in range(0, N_train, batch_size):
        adj_batch = list()
        idx_batch = list()
        y_batch = list()

        ############## Task 7
        
        ##################
        batch_graphs = G_train[i:(i+1)*batch_size]
        y_batch = torch.Tensor(y_train[i:(i+1)*batch_size]).to(device).to(torch.int64)
        # adjacency and membership
        batch_adjacencies = [nx.adjacency_matrix(G) + np.eye(G.number_of_nodes()) for G in batch_graphs]
        # membership vector indicating graph IDs
        idx_batch = torch.Tensor([i for i in range(len(batch_adjacencies)) for _ in range(len(batch_adjacencies[i]))]).to(device).to(torch.int64)
        adj_batch = sp.block_diag(batch_adjacencies) 
        features_batch = torch.ones((adj_batch.shape[0], 1)).to(device)
        adj_batch = sparse_mx_to_torch_sparse_tensor(adj_batch).to(device)
        
        
        ##################
        
        optimizer.zero_grad()
        output = model(features_batch, adj_batch, idx_batch)
        loss = loss_function(output, y_batch)
        train_loss += loss.item() * output.size(0)
        count += output.size(0)
        preds = output.max(1)[1].type_as(y_batch)
        correct += torch.sum(preds.eq(y_batch).double())
        loss.backward()
        optimizer.step()
    
    if epoch % 10 == 0:
        print('Epoch: {:04d}'.format(epoch+1),
              'loss_train: {:.4f}'.format(train_loss / count),
              'acc_train: {:.4f}'.format(correct / count),
              'time: {:.4f}s'.format(time.time() - t))
        
print('Optimization finished!')

# Evaluates the model
model.eval()
test_loss = 0
correct = 0
count = 0
for i in range(0, N_test, batch_size):
    adj_batch = list()
    idx_batch = list()
    y_batch = list()

    ############## Task 7
    
    ##################
    batch_graphs = G_test[i:(i+1)*batch_size]
    y_batch = torch.Tensor(y_test[i:(i+1)*batch_size]).to(device).to(torch.int64)
    batch_adjacencies = [nx.adjacency_matrix(G) + np.eye(G.number_of_nodes()) for G in batch_graphs]
    # membership vector indicating graph IDs
    idx_batch = torch.Tensor([i for i in range(len(batch_adjacencies)) for _ in range(len(batch_adjacencies[i]))]).to(device).to(torch.int64)
    adj_batch = sp.block_diag(batch_adjacencies) 
    features_batch = torch.ones((adj_batch.shape[0], 1)).to(device)
    adj_batch = sparse_mx_to_torch_sparse_tensor(adj_batch).to(device)

    ##################

    output = model(features_batch, adj_batch, idx_batch)
    loss = loss_function(output, y_batch)
    test_loss += loss.item() * output.size(0)
    count += output.size(0)
    preds = output.max(1)[1].type_as(y_batch)
    correct += torch.sum(preds.eq(y_batch).double())

print('loss_test: {:.4f}'.format(test_loss / count),
      'acc_test: {:.4f}'.format(correct / count),
      'time: {:.4f}s'.format(time.time() - t))

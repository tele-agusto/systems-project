'''
Functions for k-fold evaluation of models.
'''

import random
import pickle
import numpy as np
from sklearn.model_selection import KFold
import torch

import data_utils
from reggnn import RegGNN

from config import Config
import UTR as utr
import pandas as pd
import torch_geometric


def return_h5_path(file):
    path = f'/content/drive/MyDrive/{file}'
    return path


def evaluate_RegGNN(sample_selection=False, shuffle=False, random_state=None,
                    dropout=0.1, k_list=list(range(2, 16)), lr=1e-5, wd=5e-4,
                    device=torch.device('cpu'), num_epoch=200, n_select_splits=10):
    if sample_selection is False:
        k_list = [0]

    overall_preds = {k: [] for k in k_list}
    overall_scores = {k: [] for k in k_list}
    train_mae = {k: [] for k in k_list}
    
    # 5' utr adjacency matrix
    adj_t = torch.tensor(utr.adjacency)
    
##     randomly shuffled 5' utr adjacency matrix
#     dummy_1 = utr.adjacency
#     print(sum(utr.adjacency))
#     print(sum(dummy_1))
#     for i in range(len(dummy_1)):
#       dummy_1[i,:][i] -= 1

#     dummy_2 = np.array(dummy_1)
#     random.shuffle(dummy_2)

#     for i in range(len(dummy_2)):
#       dummy_2[i,:][i] += 1

#     print(sum(dummy_2))
#     adj_t = torch.tensor(dummy_2)
    
    ## fully-connected adjacency matrix
    # adj_t = torch.ones(110,110)
   
    # convert adjacency matrix to edge index
    edge_index = adj_t.nonzero().contiguous()
    edge_index = edge_index
    edge_index = edge_index.t()

    # Load data and metadata
    pd.options.display.precision = 5
    df_cite_targets = pd.read_hdf(return_h5_path('train_cite_targets.h5'))
    # df_cite_targets = df_cite_targets.iloc[0:1000,:]
    df_cite_inputs = pd.read_hdf(return_h5_path('train_cite_inputs.h5'))
    # df_cite_inputs = df_cite_inputs.iloc[0:1000,:]
    df_meta = pd.read_csv(return_h5_path('metadata.csv'), index_col='cell_id')

    # inputs_gnn = pd.read_csv('/content/drive/MyDrive/denoised_scrnaseqscimpute_count.csv',header=0,index_col=0)
    # inputs_gnn = inputs_gnn.transpose()
    
    # get indexes for samples collected from each donor on a given day
    df_meta = df_meta[df_meta.technology == 'citeseq']
    df_meta = df_meta[df_meta.day != 7]
    df_meta = df_meta[df_meta.donor != 27678]
    df_meta_2 = df_meta[df_meta.day == 2]
    df_meta_3 = df_meta[df_meta.day == 3]
    df_meta_4 = df_meta[df_meta.day == 4]
    df_meta_2_32606 = df_meta_2[df_meta_2.donor == 32606]
    df_meta_3_32606 = df_meta_3[df_meta_3.donor == 32606]
    df_meta_4_32606 = df_meta_4[df_meta_4.donor == 32606]
    df_meta_2_13176 = df_meta_2[df_meta_2.donor == 13176]
    df_meta_3_13176 = df_meta_3[df_meta_3.donor == 13176]
    df_meta_4_13176 = df_meta_4[df_meta_4.donor == 13176]
    df_meta_2_31800 = df_meta_2[df_meta_2.donor == 31800]
    df_meta_3_31800 = df_meta_3[df_meta_3.donor == 31800]
    df_meta_4_31800 = df_meta_4[df_meta_4.donor == 31800]
    # df_meta = df_meta.iloc[0:5000,:]
    print(df_meta.shape)
    
    # order inputs and targets by donor and day + drop columns of genes w/o corresponding proteins
    inputs = df_cite_inputs.loc[df_meta.index]
    targets = df_cite_targets.loc[df_meta.index]
    to_drop = [column for column in inputs.columns if column not in list(utr.utrs.Full_gene)]
    print(len(to_drop))
    inputs_gnn = inputs.drop(inputs[to_drop], axis=1)
    inputs_gnn_1 = inputs_gnn.loc[df_meta_2_32606.index]
    inputs_gnn_2 = inputs_gnn.loc[df_meta_3_32606.index]
    inputs_gnn_3 = inputs_gnn.loc[df_meta_4_32606.index]
    inputs_gnn_4 = inputs_gnn.loc[df_meta_2_13176.index]
    inputs_gnn_5 = inputs_gnn.loc[df_meta_3_13176.index]
    inputs_gnn_6 = inputs_gnn.loc[df_meta_4_13176.index]
    inputs_gnn_7 = inputs_gnn.loc[df_meta_2_31800.index]
    inputs_gnn_8 = inputs_gnn.loc[df_meta_3_31800.index]
    inputs_gnn_9 = inputs_gnn.loc[df_meta_4_31800.index]
    inputs_gnn = np.vstack((inputs_gnn_1,inputs_gnn_2,inputs_gnn_3,inputs_gnn_4,inputs_gnn_5,inputs_gnn_6,inputs_gnn_7,inputs_gnn_8,inputs_gnn_9))
    inputs_gnn = inputs_gnn[0:70656,:]
    to_drop_2 = [column for column in targets.columns if column not in list(utr.utrs.Protein)]
    print(len(to_drop_2))
    print(inputs_gnn.shape)
    targets_gnn = targets.drop(targets[to_drop_2], axis=1)
    print(targets_gnn.shape)
    targets_gnn.round(decimals=3)
    targets_gnn_1 = targets_gnn.loc[df_meta_2_32606.index]
    targets_gnn_2 = targets_gnn.loc[df_meta_3_32606.index]
    targets_gnn_3 = targets_gnn.loc[df_meta_4_32606.index]
    targets_gnn_4 = targets_gnn.loc[df_meta_2_13176.index]
    targets_gnn_5 = targets_gnn.loc[df_meta_3_13176.index]
    targets_gnn_6 = targets_gnn.loc[df_meta_4_13176.index]
    targets_gnn_7 = targets_gnn.loc[df_meta_2_31800.index]
    targets_gnn_8 = targets_gnn.loc[df_meta_3_31800.index]
    targets_gnn_9 = targets_gnn.loc[df_meta_4_31800.index]
    targets_gnn = np.vstack((targets_gnn_1,targets_gnn_2,targets_gnn_3,targets_gnn_4,targets_gnn_5,targets_gnn_6,targets_gnn_7,targets_gnn_8,targets_gnn_9))
    
    # inputs_gnn = torch.tensor(inputs_gnn.values)
    inputs_gnn = torch.tensor(inputs_gnn)
    inputs_gnn = torch.t(inputs_gnn)
    # targets_gnn = torch.tensor(targets_gnn.values)
    targets_gnn = torch.tensor(targets_gnn)
    targets_gnn = torch.t(targets_gnn)
    print(targets_gnn[0:2, 0:20])
#     cell_numbers = [0,7476,6999,9511,6071,7643,8485,8395,6259,10149]
#     cell_numbers_2 = [0,7476,14475,23986,30057,37700,46185,54580,60389,70988]
    print(inputs_gnn.shape)
    print(targets_gnn.shape)
    
    # load batches into Data object for gnn training
    pyg_data = []
    for i in range(552):
        inputs_batch = inputs_gnn[:, 128 * i:128 * (i + 1)]
        pyg_data.append(torch_geometric.data.Data(x=inputs_batch,
                                                  y=torch.round(targets_gnn[:, 128 * i:128 * (i + 1)].float(),
                                                                decimals=3), edge_index=edge_index,
                                                  edge_attr=None))

    data = pyg_data

    fold = -1
    for train_idx, test_idx in KFold(Config.K_FOLDS, shuffle=shuffle,
                                     random_state=random_state).split(data):
        fold += 1
        print(f"Cross Validation Fold {fold + 1}/{Config.K_FOLDS}")
        if sample_selection:
            sample_atlas = sampsel.select_samples(train_idx, n_select_splits, k_list,
                                                  data_dict, score_dict, shuffle,
                                                  random_state)

        for k in k_list:
            if sample_selection:
                selected_train_data = [data[subject] for subject in sample_atlas[k]]
            else:
                selected_train_data = [data[i] for i in train_idx]
            test_data = [data[i] for i in test_idx]

            # candidate_model = RegGNN(7476, 512, 110, dropout).float().to(device)
            candidate_model = RegGNN(128).float().to(device)
            optimizer = torch.optim.Adam(candidate_model.parameters(), lr=lr, weight_decay=wd)
            train_loader, test_loader = data_utils.get_loaders(selected_train_data, test_data)
            candidate_model.train()
            for epoch in range(num_epoch):
                preds = []
                scores = []
                for batch in train_loader:
                    out = candidate_model(batch.x.to(device, dtype = torch.float32), data_utils.to_dense(batch).adj.to(device, dtype=torch.int64))
                    # out = candidate_model(batch.x.to(device), data_utils.to_dense(batch).edge_index.to(device, dtype=torch.int32))
                    # loss = candidate_model.loss(out.view(-1, 1), batch.y.to(device).view(-1, 1))
                    loss = candidate_model.loss(out.reshape(-1, 1), batch.y.to(device).reshape(-1, 1))
                    if epoch % 50 == 0:
                        print(loss)

                    candidate_model.zero_grad()
                    loss.backward()
                    optimizer.step()
                    preds.append(out.cpu().data.numpy())
                    scores.append(batch.y.numpy())
                
                preds = np.hstack(preds)
                scores = np.hstack(scores)
                epoch_mae = np.mean(np.abs(preds.reshape(-1, 1) - scores.reshape(-1, 1)))
                train_mae[k].append(epoch_mae)

                for batch in test_loader:
                    out2 = candidate_model(batch.x.to(device, dtype = torch.float32),
                                          data_utils.to_dense(batch).adj.to(device, dtype=torch.int64))
                    
                    loss2 = candidate_model.loss(out2.reshape(-1, 1), batch.y.to(device).reshape(-1, 1))
                    if epoch % 50 == 0:
                      print(f'test:{loss2}')


            candidate_model.eval()
            with torch.no_grad():
                preds = []
                scores = []
                for batch in test_loader:
                    out = candidate_model(batch.x.to(device, dtype = torch.float32),
                                          data_utils.to_dense(batch).adj.to(device, dtype=torch.int64))
                   
                    loss = candidate_model.loss(out.reshape(-1, 1), batch.y.to(device).reshape(-1, 1))
                    preds.append(out.cpu().data.numpy())
                    scores.append(batch.y.cpu().numpy())

                preds = np.hstack(preds)
                scores = np.hstack(scores)

            overall_preds[k].extend(preds)
            overall_scores[k].extend(scores)

    for k in k_list:
        overall_preds[k] = np.vstack(overall_preds[k]).ravel()
        overall_scores[k] = np.vstack(overall_scores[k]).ravel()

    if sample_selection is False:
        overall_preds = overall_preds[k_list[0]]
        overall_scores = overall_scores[k_list[0]]
        overall_scores = np.around(overall_scores, decimals=3)
        print(overall_scores[0:20])

    return overall_preds, overall_scores, train_mae
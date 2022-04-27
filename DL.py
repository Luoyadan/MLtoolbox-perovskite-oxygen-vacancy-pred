import torch
import torch.nn.functional as F
import matplotlib.pyplot as plt
import pandas as pd
# torch.manual_seed(1)    # reproducible
# set precision
pd.set_option('display.precision', 14)
# import modules
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings("ignore")
from sklearn.metrics import r2_score
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from torch.utils.data import DataLoader
import random
import os
os.environ["CUDA_DEVICE_ORDER"]="PCI_BUS_ID"   
os.environ["CUDA_VISIBLE_DEVICES"]="1"

# import Co training data using the pandas library and convert them into a dataframe
raw_data = pd.read_excel('data/Co_temperature.xlsx')
raw_data.dropna(axis='rows', inplace=True)

random_state = 1
raw_data.describe()
from sklearn.utils import shuffle
# take the oxygen vacancy as the label
from torch.utils.data import Dataset
Y = raw_data.loc[:, 'Oxygen vacancy'].values

# take the other collumns as the features
X = raw_data.iloc[:, 3:]


X, y = shuffle(X, Y, random_state=random_state)
X.head()





# # read Fe training data
# data_fe = pd.read_excel('data/Fe_temperature.xlsx')
# data_fe.dropna(axis='rows', inplace=True)
# Y_fe = data_fe.loc[:, 'Oxygen vacancy'].values

# # take the other collumns as the features and do shuffle
# X_fe = data_fe.iloc[:, 3:]

# X_fe, y_fe = shuffle(X_fe, Y_fe, random_state=random_state)

class CoDataset(Dataset):
    def __init__(self, X_train, y_train):
        self.X_train = X_train
        self.y_train = y_train
    
    def __getitem__(self, index):

        return self.X_train[index, :], self.y_train[index]


    def __len__(self):
        return X_train.shape[0]

X = X.to_numpy()

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=random_state)

X_train, X_test, y_train = torch.from_numpy(X_train).float(), torch.from_numpy(X_test).float(), torch.from_numpy(y_train).float()


co_data = CoDataset(X_train, y_train)
dataloader = DataLoader(co_data, batch_size=1, shuffle=True)


class Net(torch.nn.Module):
    def __init__(self, n_feature, n_hidden, n_output):
        super(Net, self).__init__()
        self.hidden = torch.nn.Linear(n_feature, n_hidden)
        self.activation = torch.nn.PReLU()
        self.predict = torch.nn.Linear(n_hidden, n_output)   # output layer

    def forward(self, x):
        x = self.activation(self.hidden(x))     # activation function for hidden layer
        x = self.predict(x)             # linear output
        return x

net = Net(n_feature=X_train.shape[-1], n_hidden=100, n_output=1)     # define the network
print(net)  # net architecture

optimizer = torch.optim.SGD(net.parameters(), lr=1e-3)
loss_func = torch.nn.MSELoss()  # this is for regression mean squared loss


net.train()
for t in range(500):
    # temp = list(zip(X_train, y_train))
    # random.shuffle(temp)
    # X_train, y_train = zip(*temp)
    # X_train, y_train = torch.stack(X_train, 0), torch.stack(y_train)
    for batch_x, batch_y in dataloader:
        
        prediction = net(batch_x)     # input x and predict based on x

        loss = loss_func(prediction, batch_y)     # must be (1. nn output, 2. target)

        optimizer.zero_grad()   # clear gradients for next train
        loss.backward()         # backpropagation, compute gradients
        optimizer.step()        # apply gradients
        # if i % 100 == 0:
        #     print('Ep {} Iter {} - training error: {}'.format(t, i, loss))

    if t % 10 == 0:
        net.eval()
        eval_list = []
        for j in range(X_test.shape[0]):
            prediction = net(X_test[j, :])
            eval_list.append(prediction.detach().cpu().numpy())
        # plot and show learning process

        mse = mean_squared_error(y_test, np.array(eval_list))
        r2 = r2_score(y_test, np.array(eval_list))
        print('Evaluationg Ep {}: MSE {}, R^2 {}'.format(t, mse, r2))

        net.train()


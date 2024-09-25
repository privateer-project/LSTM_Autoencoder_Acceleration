import torch
import torch.nn as nn
import torch.optim as optim

class Encoder(nn.Module):
    def __init__(self, input_dim, hidden_dim1, hidden_dim2, dropout, layer_norm_flag):
        super(Encoder, self).__init__()
        self.lstm1 = nn.LSTM(input_dim, hidden_dim1, num_layers=2, batch_first=True, dropout = dropout)
        self.lstm2 = nn.LSTM(hidden_dim1, hidden_dim2, num_layers=2,  batch_first=True, dropout = dropout)
        self.layer_norm_flag = layer_norm_flag
        self.layer_norm = nn.LayerNorm(hidden_dim2)
    
    def forward(self, x):
        x, _ = self.lstm1(x)
        x, (hidden, _) = self.lstm2(x)
        if self.layer_norm_flag:
            x = self.layer_norm(x)
        return x

class Decoder(nn.Module):
    def __init__(self, encoded_dim, hidden_dim1, output_dim, dropout):
        super(Decoder, self).__init__()
        self.lstm1 = nn.LSTM(encoded_dim, hidden_dim1, num_layers=2, batch_first=True, dropout = dropout)
        self.lstm2 = nn.LSTM(hidden_dim1, output_dim, num_layers=2, batch_first=True, dropout = dropout)
    
    def forward(self, x):
        x, _ = self.lstm1(x)
        x, _ = self.lstm2(x)
        return x

class LSTMAutoencoder(nn.Module):
    def __init__(
        self, 
        input_dim, 
        hidden_dim1, 
        hidden_dim2, 
        output_dim, 
        dropout, 
        layer_norm_flag
    ):
        super(LSTMAutoencoder, self).__init__()
        self.encoder = Encoder(input_dim, hidden_dim1, hidden_dim2, dropout, layer_norm_flag)
        self.decoder = Decoder(hidden_dim2, hidden_dim1, output_dim, dropout)
    
    def forward(self, x):
        encoded = self.encoder(x)
        decoded = self.decoder(encoded)
        return decoded
    
    def encode(self, x):
        encoded = self.encoder(x)
        return encoded
    
    def decode(self, x):
        decoded = self.decoder(x)
        return decoded
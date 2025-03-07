import torch
import torch.nn as nn
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class PricePredictor(nn.Module):
    def __init__(self, input_dim=1, d_model=128, n_heads=8, n_layers=4, dropout=0.1):
        super(PricePredictor, self).__init__()
        self.input_embedding = nn.Linear(input_dim, d_model)
        self.pos_encoding = self.positional_encoding(1000, d_model)
        encoder_layer = nn.TransformerEncoderLayer(d_model=d_model, nhead=n_heads, dropout=dropout)
        self.transformer_encoder = nn.TransformerEncoder(encoder_layer, num_layers=n_layers)
        self.fc = nn.Linear(d_model, 1)
        self.dropout = nn.Dropout(dropout)

    def positional_encoding(self, seq_len, d_model):
        pe = torch.zeros(seq_len, d_model)
        position = torch.arange(0, seq_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * (-np.log(10000.0) / d_model))
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        return pe.unsqueeze(0)

    def forward(self, x):
        batch_size, seq_len, _ = x.size()
        x = self.input_embedding(x)
        x += self.pos_encoding[:, :seq_len, :].to(x.device)
        x = self.dropout(x)
        x = self.transformer_encoder(x)
        x = self.fc(x[:, -1, :])
        return x

class PricePredictor:
    def __init__(self):
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = PricePredictor().to(self.device)
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=0.0005)
        self.criterion = nn.MSELoss()

    def prepare_data(self, df):
        data = df['close'].values.reshape(-1, 1)
        scaled_data = self.scaler.fit_transform(data)
        seq_length = 50
        X, y = [], []
        for i in range(seq_length, len(scaled_data)):
            X.append(scaled_data[i-seq_length:i])
            y.append(scaled_data[i])
        X = torch.tensor(X, dtype=torch.float32).to(self.device)
        y = torch.tensor(y, dtype=torch.float32).to(self.device)
        return X, y

    def train(self, df):
        X, y = self.prepare_data(df)
        self.model.train()
        for epoch in range(15):
            self.optimizer.zero_grad()
            output = self.model(X)
            loss = self.criterion(output, y)
            loss.backward()
            self.optimizer.step()
            logging.info(f"Epoch {epoch+1}, Loss: {loss.item()}")

    def predict(self, df):
        self.model.eval()
        X, _ = self.prepare_data(df)
        with torch.no_grad():
            last_seq = X[-1].unsqueeze(0)
            pred_scaled = self.model(last_seq)
            pred = self.scaler.inverse_transform(pred_scaled.cpu().numpy())
        return pred[0][0]

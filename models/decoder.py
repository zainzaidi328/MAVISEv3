import torch
import torch.nn as nn

class SpectrogramDecoder(nn.Module):
    def __init__(self, in_channels=128, out_dim=257):
        super(SpectrogramDecoder, self).__init__()
        # Decodes back to F dimensions
        self.lstm = nn.LSTM(input_size=in_channels, hidden_size=256, batch_first=True, bidirectional=True)
        self.linear1 = nn.Linear(512, 512)
        self.relu = nn.ReLU()
        self.linear2 = nn.Linear(512, out_dim)
        self.sigmoid = nn.Sigmoid()
        
    def forward(self, x):
        # x: (B, T, in_channels)
        out, _ = self.lstm(x)
        out = self.relu(self.linear1(out))
        mask = self.sigmoid(self.linear2(out))
        # Mask shape: (B, T, F)
        # Permute to match spectrogram (B, 1, F, T)
        mask = mask.permute(0, 2, 1).unsqueeze(1)
        return mask

import torch
import torch.nn as nn

class AudioEncoder(nn.Module):
    def __init__(self, input_dim=257, out_channels=128):
        # input_dim: No of Frequency bins (e.g. 257 for n_fft=512)
        super(AudioEncoder, self).__init__()
        self.conv1 = nn.Conv2d(1, 32, kernel_size=(3, 3), padding=(1, 1))
        self.bn1 = nn.BatchNorm2d(32)
        self.relu = nn.ReLU()
        
        self.conv2 = nn.Conv2d(32, 64, kernel_size=(3, 3), padding=(1, 1))
        self.bn2 = nn.BatchNorm2d(64)
        
        # Flatten freq dimension for LSTM. If input is F=257, 64 channels => 64*257 = 16448. Need pooling.
        self.pool = nn.MaxPool2d((4, 1)) # Downsample frequency by 4, keep time
        # F becomes roughly 64
        self.pool2 = nn.MaxPool2d((2, 1)) 
        # F becomes roughly 32, then 64 channels * 32 = 2048
        
        lstm_input_dim = 64 * (input_dim // 8) # Approx depending on actual F
        
        self.lstm = nn.LSTM(input_size=lstm_input_dim, hidden_size=out_channels, batch_first=True, bidirectional=True)
        self.linear = nn.Linear(out_channels * 2, out_channels)
        
    def forward(self, x):
        # x: (B, 1, F, T) -> Magnitude Spectrogram
        B, C, F, T = x.size()
        
        out = self.relu(self.bn1(self.conv1(x)))
        out = self.pool(out)
        out = self.relu(self.bn2(self.conv2(out)))
        out = self.pool2(out) # (B, 64, F', T)
        
        B, C_new, F_new, T_new = out.size()
        
        # Guard against zero-length sequences
        if T_new == 0 or out.numel() == 0:
            return torch.zeros(B, T, self.linear.out_features).to(x.device)
        
        out = out.permute(0, 3, 1, 2).contiguous() # (B, T, 64, F')
        out = out.view(B, T_new, -1) # (B, T, feat_dim)
        
        lstm_out, _ = self.lstm(out)
        out = self.linear(lstm_out) # (B, T, out_channels)
        return out

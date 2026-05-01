import torch
import torch.nn as nn

class VideoEncoder(nn.Module):
    def __init__(self, out_channels=128):
        super(VideoEncoder, self).__init__()
        # Input: (B, 3, T, H, W) where H=96, W=96
        self.conv3d_1 = nn.Conv3d(3, 32, kernel_size=(5, 5, 5), padding=(2, 2, 2))
        self.bn1 = nn.BatchNorm3d(32)
        self.relu = nn.ReLU()
        self.pool1 = nn.MaxPool3d((1, 2, 2)) # Keep time, downsample spatial (96->48)
        
        self.conv3d_2 = nn.Conv3d(32, 64, kernel_size=(3, 3, 3), padding=(1, 1, 1))
        self.bn2 = nn.BatchNorm3d(64)
        self.pool2 = nn.MaxPool3d((1, 2, 2)) # (48->24)
        
        self.conv3d_3 = nn.Conv3d(64, 128, kernel_size=(3, 3, 3), padding=(1, 1, 1))
        self.bn3 = nn.BatchNorm3d(128)
        self.pool3 = nn.MaxPool3d((1, 4, 4)) # (24->6)
        
        self.fc = nn.Linear(128 * 6 * 6, out_channels)
        
    def forward(self, x):
        B, C, T, H, W = x.size()
        out = self.relu(self.bn1(self.conv3d_1(x)))
        out = self.pool1(out)
        
        out = self.relu(self.bn2(self.conv3d_2(out)))
        out = self.pool2(out)
        
        out = self.relu(self.bn3(self.conv3d_3(out)))
        out = self.pool3(out)
        
        B, C_out, T_out, H_out, W_out = out.size()
        
        # Guard against zero-length sequences to prevent reshape errors
        if T_out == 0 or out.numel() == 0:
            return torch.zeros(B, T, self.fc.out_features).to(x.device)
            
        out = out.permute(0, 2, 1, 3, 4).contiguous() # (B, T, C, H, W)
        out = out.view(B, T_out, -1) # (B, T, features)
        
        out = self.fc(out) # (B, T, out_channels)
        return out

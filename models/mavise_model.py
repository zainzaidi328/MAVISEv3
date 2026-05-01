import torch
import torch.nn as nn
from .audio_encoder import AudioEncoder
from .video_encoder import VideoEncoder
from .fusion import CrossModalFusion
from .decoder import SpectrogramDecoder

class MAVISEGenerator(nn.Module):
    def __init__(self, n_fft=512):
        super(MAVISEGenerator, self).__init__()
        # For n_fft=512, F=257
        F_dim = n_fft // 2 + 1
        self.audio_encoder = AudioEncoder(input_dim=F_dim, out_channels=128)
        self.video_encoder = VideoEncoder(out_channels=128)
        self.fusion = CrossModalFusion(audio_dim=128, video_dim=128, fused_dim=128)
        self.decoder = SpectrogramDecoder(in_channels=128, out_dim=F_dim)
        
    def forward(self, noisy_mag, video_frames):
        # noisy_mag: (B, 1, F, T) magnitude spectrogram
        # video_frames: (B, T_v, C, H, W)
        
        # 1. Video encoder expects (B, 3, T_v, H, W)
        video_frames = video_frames.permute(0, 2, 1, 3, 4).contiguous()
        
        # 2. Extract features
        audio_feat = self.audio_encoder(noisy_mag)
        video_feat = self.video_encoder(video_frames)
        
        # 3. Fuse
        fused_feat = self.fusion(audio_feat, video_feat)
        
        # 4. Decode to get mask
        mask = self.decoder(fused_feat)
        
        # 5. Apply magnitude mask (Ideal Ratio Mask)
        clean_mag = noisy_mag * mask
        
        return clean_mag, mask

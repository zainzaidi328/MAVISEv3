import torch
import torch.nn as nn
import torch.nn.functional as F

class CrossModalFusion(nn.Module):
    def __init__(self, audio_dim=128, video_dim=128, fused_dim=128):
        super(CrossModalFusion, self).__init__()
        self.linear1 = nn.Linear(audio_dim + video_dim, fused_dim)
        self.relu = nn.ReLU()
        
        # Simple attention or transformer
        encoder_layer = nn.TransformerEncoderLayer(d_model=fused_dim, nhead=4, batch_first=True, dim_feedforward=512)
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=2)
        
    def forward(self, audio_feat, video_feat):
        # audio_feat: (B, T_a, C_a)
        # video_feat: (B, T_v, C_v)
        
        B, T_a, C_a = audio_feat.size()
        B, T_v, C_v = video_feat.size()
        
        if T_a == 0:
            return torch.zeros(B, 0, self.linear1.out_features).to(audio_feat.device)
            
        if T_v == 0:
            # Handle case where video has no frames but audio exists
            video_feat = torch.zeros(B, T_a, C_v).to(audio_feat.device)
        else:
            # Interpolate video features to match audio time dimension
            # (B, C_v, T_v) -> target (B, C_v, T_a)
            video_feat = video_feat.permute(0, 2, 1)
            if T_v > 1:
                video_feat = F.interpolate(video_feat, size=T_a, mode='linear', align_corners=False)
            else:
                # If only 1 video frame, repeat it
                video_feat = video_feat.repeat(1, 1, T_a)
            video_feat = video_feat.permute(0, 2, 1) # back to (B, T_a, C_v)
        
        # Concatenate along feature dim
        fused = torch.cat([audio_feat, video_feat], dim=-1) # (B, T_a, C_a + C_v)
        fused = self.relu(self.linear1(fused))
        
        # Pass through Transformer
        fused = self.transformer(fused)
        
        return fused
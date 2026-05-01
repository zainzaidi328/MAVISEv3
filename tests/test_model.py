import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import torch
from models.mavise_model import MAVISEGenerator

def test():
    print("Testing MAVISE Generator Forward Pass...")
    model = MAVISEGenerator(n_fft=512)
    model.eval()
    
    noisy_mag = torch.rand(2, 1, 257, 100) # (B, 1, F, T)
    video_frames = torch.rand(2, 100, 3, 96, 96) # (B, T_v, C, H, W)
    
    with torch.no_grad():
        clean_mag, mask = model(noisy_mag, video_frames)
        
    print(f"Clean Mag Shape: {clean_mag.shape}")
    print(f"Mask Shape: {mask.shape}")
    if clean_mag.shape == noisy_mag.shape:
        print("Success: Shape matching verified.")
    else:
        print("Failed: Output shape mismatch!")

if __name__ == "__main__":
    test()

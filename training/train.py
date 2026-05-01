import os
import sys

# Add project root to sys.path so modules can be imported directly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import torch
import torch.optim as optim
from torch.utils.tensorboard import SummaryWriter
from tqdm import tqdm
from data.dataset import get_dataloader
from models.mavise_model import MAVISEGenerator
from training.losses import MaviseLoss

def train_model(data_dir, epochs=50, batch_size=4, lr=1e-4, save_dir="checkpoints"):
    os.makedirs(save_dir, exist_ok=True)
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    
    # Init dataloader, model, loss, optimizer
    # Notice num_workers=0 to avoid multiprocessing issues on windows simply
    train_loader = get_dataloader(data_dir, batch_size=batch_size, is_train=True, num_workers=0)
    
    model = MAVISEGenerator(n_fft=512).to(device)
    criterion = MaviseLoss(alpha=0.5).to(device)
    optimizer = optim.Adam(model.parameters(), lr=lr)
    
    writer = SummaryWriter(log_dir=os.path.join(save_dir, "logs"))
    print("Starting training...")
    
    for epoch in range(epochs):
        model.train()
        epoch_loss = 0.0
        pbar = tqdm(train_loader, desc=f"Epoch {epoch+1}/{epochs}")
        
        for batch_idx, (noisy_audio, clean_audio, video_frames) in enumerate(pbar):
            noisy_audio = noisy_audio.to(device)
            clean_audio = clean_audio.to(device)
            video_frames = video_frames.to(device)
            
            optimizer.zero_grad()
            
            # STFT processing
            window = torch.hann_window(400).to(device)
            noisy_stft = torch.stft(noisy_audio.squeeze(1), n_fft=512, hop_length=160, win_length=400, return_complex=True, window=window)
            clean_stft = torch.stft(clean_audio.squeeze(1), n_fft=512, hop_length=160, win_length=400, return_complex=True, window=window)
            
            noisy_mag = torch.abs(noisy_stft).unsqueeze(1) # (B, 1, F, T)
            clean_mag = torch.abs(clean_stft).unsqueeze(1)
            
            # Forward
            est_mag, mask = model(noisy_mag, video_frames)
            
            # Loss (only L1 on magnitude in this simplified setup)
            loss, l1, snr = criterion(est_mag, clean_mag)
            
            loss.backward()
            optimizer.step()
            
            epoch_loss += loss.item()
            pbar.set_postfix({'loss': loss.item()})
            
            writer.add_scalar("Loss/train_step", loss.item(), epoch * len(train_loader) + batch_idx)
            
        avg_loss = epoch_loss / len(train_loader)
        print(f"Epoch {epoch+1} Average Loss: {avg_loss:.4f}")
        writer.add_scalar("Loss/train_epoch", avg_loss, epoch)
        
        # Save checkpoint
        torch.save(model.state_dict(), os.path.join(save_dir, f"mavise_epoch_{epoch+1}.pth"))

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_dir", type=str, required=True, help="Path to data directory")
    args = parser.parse_args()
    train_model(args.data_dir)

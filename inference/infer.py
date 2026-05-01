import os
import sys

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import torch
import torchaudio
import numpy as np
import cv2
from models.mavise_model import MAVISEGenerator
from data.preprocess_audio import load_audio
from data.preprocess_video import process_video

class MaviseInferencer:
    def __init__(self, checkpoint_path, device='cpu'):
        self.device = torch.device(device)
        self.model = MAVISEGenerator(n_fft=512).to(self.device)
        if os.path.exists(checkpoint_path):
            self.model.load_state_dict(torch.load(checkpoint_path, map_location=self.device))
            print(f"Loaded checkpoint from {checkpoint_path}")
        else:
            print("Checkpoint not found, using uninitialized model.")
        
        self.model.eval()
        
    def enhance(self, video_path, audio_path=None):
        # If audio path is not provided, automatically extract from video using moviepy
        if not audio_path:
            try:
                from moviepy.editor import VideoFileClip
                input_audio_path = video_path + "_extracted.wav"
                clip = VideoFileClip(video_path)
                if clip.audio is not None:
                    clip.audio.write_audiofile(input_audio_path, logger=None)
                else:
                    input_audio_path = video_path
                clip.close()
            except Exception as e:
                print(f"Moviepy extraction failed: {e}")
                input_audio_path = video_path
        else:
            input_audio_path = audio_path
        
        # 1. Process Video
        video_frames = process_video(video_path, target_size=(96, 96)) # (T, C, H, W)
        if video_frames.shape[0] == 0:
            raise ValueError("No frames extracted from video")
            
        video_tensor = torch.from_numpy(video_frames).unsqueeze(0).to(self.device) # (1, T, C, H, W)
        
        # 2. Process Audio
        try:
            noisy_audio = load_audio(input_audio_path, target_sr=16000) # (1, Time)
        except Exception as e:
            raise ValueError(f"Failed to load audio: {e}")
            
        # Length matching based on video
        max_frames = video_tensor.shape[1]
        if max_frames == 0:
            raise ValueError("Video has 0 frames after processing.")
            
        expected_audio_samples = int(max_frames * (16000 / 25.0))
        if expected_audio_samples == 0:
            raise ValueError("Video is too short for audio synchronization.")
        
        if noisy_audio.shape[1] > expected_audio_samples:
            noisy_audio = noisy_audio[:, :expected_audio_samples]
        elif noisy_audio.shape[1] < expected_audio_samples:
            pad = expected_audio_samples - noisy_audio.shape[1]
            noisy_audio = torch.nn.functional.pad(noisy_audio, (0, pad))
            
        noisy_audio = noisy_audio.unsqueeze(0).to(self.device) # (1, 1, Time)
        
        # STFT
        window = torch.hann_window(400).to(self.device)
        noisy_stft = torch.stft(noisy_audio.squeeze(1), n_fft=512, hop_length=160, win_length=400, return_complex=True, window=window)
        noisy_mag = torch.abs(noisy_stft).unsqueeze(1) # (1, 1, F, T_stft)
        noisy_phase = torch.angle(noisy_stft)
        
        # 3. Model Forward
        with torch.no_grad():
            clean_mag, mask = self.model(noisy_mag, video_tensor)
            
        # 4. Inverse STFT with Original Phase
        clean_mag_sq = clean_mag.squeeze(0).squeeze(0) # (F, T_stft)
        noisy_phase_sq = noisy_phase.squeeze(0) # (F, T_stft)
        
        # Reconstruct complex STFT
        complex_stft = clean_mag_sq * torch.exp(1j * noisy_phase_sq)
        
        # Inverse STFT
        enhanced_waveform = torch.istft(complex_stft, n_fft=512, hop_length=160, win_length=400, window=window)
        
        # VOLUME NORMALIZATION: Match original audio's peak amplitude
        orig_max = noisy_audio.abs().max()
        enh_max = enhanced_waveform.abs().max()
        if enh_max > 0 and orig_max > 0:
            enhanced_waveform = enhanced_waveform * (orig_max / enh_max)
        
        return enhanced_waveform.cpu().unsqueeze(0) # (1, Time)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--video", required=True)
    parser.add_argument("--audio", required=False)
    parser.add_argument("--output", default="enhanced.wav")
    parser.add_argument("--ckpt", default="checkpoints/mavise_epoch_50.pth")
    args = parser.parse_args()
    
    inferencer = MaviseInferencer(args.ckpt)
    waveform = inferencer.enhance(args.video, args.audio)
    import soundfile as sf
    sf.write(args.output, waveform.squeeze().cpu().numpy(), 16000)
    print(f"Saved enhanced audio to {args.output}")

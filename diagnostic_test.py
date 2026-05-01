import os
import sys
import uuid
import shutil

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from inference.infer import MaviseInferencer
import whisper

print("--- DIAGNOSTIC START ---")

# 1. Setup
TEMP_DIR = "temp_uploads"
req_id = "test_diag_" + str(uuid.uuid4().hex[:4])
video_path = os.path.join(TEMP_DIR, "test_video.mp4")

# Check if a test video exists, if not use a dummy or skip
recent_vids = [f for f in os.listdir(TEMP_DIR) if f.endswith(".mp4") and "enhanced" not in f]
if not recent_vids:
    print("No test video found in temp_uploads. Please upload one first.")
    sys.exit(1)

video_path = os.path.join(TEMP_DIR, recent_vids[0])
print(f"Using test video: {video_path}")

# 2. Load Models
try:
    ckpt_path = "checkpoints/mavise_epoch_50.pth"
    inferencer = MaviseInferencer(ckpt_path, device='cpu')
    whisper_model = whisper.load_model("tiny")
    print("Models loaded successfully.")
except Exception as e:
    print(f"FAILED to load models: {e}")
    sys.exit(1)

# 3. Process
try:
    print("Running inference...")
    out_audio_path = os.path.join(TEMP_DIR, f"{req_id}_enhanced.wav")
    waveform = inferencer.enhance(video_path)
    import soundfile as sf
    sf.write(out_audio_path, waveform.squeeze().cpu().numpy(), 16000)
    print("Inference done.")

    print("Generating subtitles...")
    vtt_name = f"{req_id}_subtitles.vtt"
    vtt_path = os.path.join(TEMP_DIR, vtt_name)
    import whisper.utils
    result = whisper_model.transcribe(out_audio_path, fp16=False)
    vtt_writer = whisper.utils.get_writer("vtt", TEMP_DIR)
    vtt_writer(result, vtt_name.replace(".vtt", ""), {})
    print(f"Subtitles generated: {vtt_path}")

    print("Attempting burn-in merge...")
    out_video_path = os.path.join(TEMP_DIR, f"{req_id}_enhanced.mp4")
    rel_vtt_path = os.path.join(TEMP_DIR, vtt_name).replace("\\", "/")
    
    import subprocess
    cmd = [
        'ffmpeg', '-y', '-i', video_path, '-i', out_audio_path,
        '-vf', f"subtitles={rel_vtt_path}",
        '-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '22',
        '-c:a', 'aac', '-b:a', '192k',
        '-map', '0:v:0', '-map', '1:a:0',
        out_video_path
    ]
    print(f"Running command: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)
    print(f"SUCCESS: {out_video_path}")

except Exception as e:
    print(f"ERROR DURING PROCESS: {e}")
    import traceback
    traceback.print_exc()

print("--- DIAGNOSTIC END ---")

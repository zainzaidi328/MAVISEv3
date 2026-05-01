# MAVISE - Multimodal Audio-Visual Speech Enhancement

Enhance noisy speech using both audio and visual inputs (lip movements) to output clean speech.

## Features
- **Deep Learning Architecture:** CNN + BiLSTM + Transformers for encoding and fusion.
- **Data processing:** Syncs frames and audio inputs, uses MediaPipe for lip crop.
- **API and UI:** Easy-to-use FastAPI backend interacting with a Streamlit web interface.

## Setup Instructions
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   **Note**: Ensure PyTorch is installed with proper CUDA support if using GPU.

2. Run Training:
   Place your videos (`.mp4`) in `data/` and run:
   ```bash
   python training/train.py --data_dir data/
   ```

3. Run API:
   ```bash
   uvicorn api.main:app --reload
   ```

4. Run Frontend:
   Open a new terminal and run:
   ```bash
   streamlit run frontend/app.py
   ```

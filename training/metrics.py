import torch
try:
    from torchmetrics.audio import PerceptualEvaluationSpeechQuality as PESQ
    from torchmetrics.audio import ShortTimeObjectiveIntelligibility as STOI
except ImportError:
    PESQ = None
    STOI = None

class Evaluator:
    def __init__(self, sr=16000, device='cpu'):
        self.sr = sr
        self.device = device
        
        # Initialize metrics if available
        if PESQ is not None and STOI is not None:
            self.pesq = PESQ(16000, 'wb').to(device)
            self.stoi = STOI(16000).to(device)
        else:
            self.pesq = None
            self.stoi = None
            
    def compute_metrics(self, est_wave, ref_wave):
        """
        est_wave: (B, T) or (T)
        ref_wave: (B, T) or (T)
        """
        metrics = {}
        if self.pesq is not None and self.stoi is not None:
            est_wave = est_wave.to(self.device).squeeze()
            ref_wave = ref_wave.to(self.device).squeeze()
            
            if est_wave.dim() == 1:
                est_wave = est_wave.unsqueeze(0)
                ref_wave = ref_wave.unsqueeze(0)
                
            try:
                pesq_score = self.pesq(est_wave, ref_wave)
                stoi_score = self.stoi(est_wave, ref_wave)
                metrics['pesq'] = pesq_score.item()
                metrics['stoi'] = stoi_score.item()
            except Exception as e:
                print(f"Error computing metrics: {e}")
                metrics['pesq'] = 0.0
                metrics['stoi'] = 0.0
        return metrics

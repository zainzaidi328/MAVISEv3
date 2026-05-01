import torch
import torch.nn as nn

def si_snr_loss(estimated: torch.Tensor, reference: torch.Tensor, eps=1e-8):
    """
    Compute Scale-Invariant Signal-to-Noise Ratio (SI-SNR).
    estimated: (B, T)
    reference: (B, T)
    Returns scalar loss (negative SI-SNR).
    """
    reference = reference - torch.mean(reference, dim=-1, keepdim=True)
    estimated = estimated - torch.mean(estimated, dim=-1, keepdim=True)
    
    ref_energy = torch.sum(reference ** 2, dim=-1, keepdim=True) + eps
    proj = torch.sum(reference * estimated, dim=-1, keepdim=True) * reference / ref_energy
    noise = estimated - proj
    
    ratio = torch.sum(proj ** 2, dim=-1) / (torch.sum(noise ** 2, dim=-1) + eps)
    si_snr = 10 * torch.log10(ratio + eps)
    return -torch.mean(si_snr)

class MaviseLoss(nn.Module):
    def __init__(self, alpha=0.5):
        super(MaviseLoss, self).__init__()
        self.alpha = alpha
        self.l1_loss = nn.L1Loss()
        
    def forward(self, est_mag, ref_mag, est_wave=None, ref_wave=None):
        # L1 loss on spectrograms
        loss_mag = self.l1_loss(est_mag, ref_mag)
        
        # SI-SNR loss on waveforms if provided
        if est_wave is not None and ref_wave is not None:
            loss_snr = si_snr_loss(est_wave, ref_wave)
            return loss_mag + self.alpha * loss_snr, loss_mag, loss_snr
            
        return loss_mag, loss_mag, torch.tensor(0.0)

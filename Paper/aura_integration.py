import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F


LABEL_MAP = {
    0: "background",
    1: "cartilage",
    2: "meniscus",
    3: "bone",
}


class Conv3DBlock(nn.Module):
    """Compact 3D encoder block modeled on the archived U-Net notes."""

    def __init__(self, in_channels: int, out_channels: int):
        super().__init__()
        self.block = nn.Sequential(
            nn.Conv3d(in_channels, out_channels, kernel_size=3, padding=1, bias=False),
            nn.GroupNorm(8, out_channels),
            nn.GELU(),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.block(x)


class MultiTaskKneeNet(nn.Module):
    """Simple 3D multi-task model for segmentation and diagnosis.

    The architecture follows the archived notebook structure: a U-Net-like
    encoder/decoder with skip connections for voxel-wise segmentation and a
    classification head for pathology detection.
    """

    def __init__(self, in_channels: int = 1, num_classes: int = 4, num_diagnoses: int = 2):
        super().__init__()
        self.num_classes = num_classes
        self.num_diagnoses = num_diagnoses

        self.stem = Conv3DBlock(in_channels, 16)
        self.encoder1 = nn.Sequential(Conv3DBlock(16, 16), Conv3DBlock(16, 16))
        self.pool1 = nn.MaxPool3d(2)

        self.encoder2 = nn.Sequential(Conv3DBlock(16, 32), Conv3DBlock(32, 32))
        self.pool2 = nn.MaxPool3d(2)

        self.bottleneck = nn.Sequential(Conv3DBlock(32, 64), Conv3DBlock(64, 64))

        self.up2 = nn.ConvTranspose3d(64, 32, kernel_size=2, stride=2)
        self.decoder2 = nn.Sequential(Conv3DBlock(64, 32), Conv3DBlock(32, 32))

        self.up1 = nn.ConvTranspose3d(32, 16, kernel_size=2, stride=2)
        self.decoder1 = nn.Sequential(Conv3DBlock(32, 16), Conv3DBlock(16, 16))

        self.segmentation_head = nn.Conv3d(16, num_classes, kernel_size=1)

        self.diagnosis_head = nn.Sequential(
            nn.AdaptiveAvgPool3d(1),
            nn.Flatten(),
            nn.Linear(64, 32),
            nn.GELU(),
            nn.Linear(32, num_diagnoses),
        )

    def forward(self, x: torch.Tensor):
        x0 = self.stem(x)
        e1 = self.encoder1(x0)
        x = self.pool1(e1)

        e2 = self.encoder2(x)
        x = self.pool2(e2)

        x = self.bottleneck(x)

        x = self.up2(x)
        x = torch.cat([x, e2], dim=1)
        x = self.decoder2(x)

        x = self.up1(x)
        x = torch.cat([x, e1], dim=1)
        x = self.decoder1(x)

        seg_logits = self.segmentation_head(x)
        diag_logits = self.diagnosis_head(x)
        return seg_logits, diag_logits


def estimate_volume_mm3(seg_mask: torch.Tensor, spacing_mm: tuple[float, float, float]) -> float:
    """Compute the total absolute volume for a foreground label."""
    spacing = np.asarray(spacing_mm, dtype=np.float32)
    voxel_volume_mm3 = float(np.prod(spacing))
    mask_np = seg_mask.detach().cpu().numpy()
    voxel_count = float(np.count_nonzero(mask_np))
    return voxel_count * voxel_volume_mm3


def build_clinical_report(
    seg_logits: torch.Tensor,
    diag_logits: torch.Tensor,
    spacing_mm: tuple[float, float, float] = (0.4, 0.4, 0.4),
    diagnosis_labels: tuple[str, str] = ("normal", "abnormal"),
):
    """Build a compact clinical-style summary from model outputs."""
    seg_mask = torch.argmax(seg_logits, dim=1, keepdim=True)
    diagnosis_prob = F.softmax(diag_logits, dim=1)
    diag_class = int(torch.argmax(diagnosis_prob, dim=1).item())
    confidence = float(diagnosis_prob[0, diag_class].item())

    metrics = {}
    for label_id, label_name in LABEL_MAP.items():
        if label_name == "background":
            continue
        label_mask = seg_mask == label_id
        voxel_count = int(label_mask.sum().item())
        metrics[label_name] = {
            "voxels": voxel_count,
            "volume_mm3": estimate_volume_mm3(label_mask, spacing_mm),
        }

    report = {
        "diagnosis": {
            "predicted_label": diagnosis_labels[diag_class],
            "confidence": confidence,
            "raw_logits": diag_logits[0].detach().cpu().tolist(),
        },
        "segmentation": {
            "mask_shape": list(seg_mask.shape),
            "classes": LABEL_MAP,
        },
        "metrics": metrics,
        "explanation": (
            f"The model suggests a {diagnosis_labels[diag_class]} finding with "
            f"{confidence:.2%} confidence. Segmentation shows localized volumes in "
            f"{', '.join(sorted(metrics.keys())) or 'no structures'} based on the voxel mask."
        ),
    }
    return report


def run_demo(volume_shape: tuple[int, int, int, int, int] = (1, 1, 16, 64, 64)) -> dict:
    """Run a small synthetic inference example inspired by the archived research note."""
    model = MultiTaskKneeNet()
    model.eval()

    with torch.no_grad():
        volume = torch.rand(*volume_shape)
        seg_logits, diag_logits = model(volume)
        report = build_clinical_report(seg_logits, diag_logits)

    return report


if __name__ == "__main__":
    report = run_demo()
    print("Diagnosis:", report["diagnosis"])
    print("Metrics:", report["metrics"])
    print("Explanation:", report["explanation"])

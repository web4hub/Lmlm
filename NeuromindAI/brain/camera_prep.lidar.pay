# Camera preprocessing
transform = transforms.Compose([
    transforms.ToPILImage(),
    transforms.Resize((224,224)),
    transforms.ToTensor()
])

def preprocess_camera(frame):
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame = transform(frame).unsqueeze(0)
    return frame

# LiDAR preprocessing
def process_lidar(scan_data):
    # scan_data: list of 360 distances
    return torch.tensor([scan_data], dtype=torch.float32)

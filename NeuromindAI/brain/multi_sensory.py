class NeurobotBrain(nn.Module):
    def __init__(self):
        super(NeurobotBrain, self).__init__()
        
        # Vision module (pretrained CNN)
        self.cnn = models.resnet18(weights=None)  # Load weights=None for training
        self.cnn.fc = nn.Linear(self.cnn.fc.in_features, 32)  # output features
        
        # Distance + IMU input
        self.sensor_fc1 = nn.Linear(2, 16)
        self.sensor_fc2 = nn.Linear(16, 16)
        
        # Combined fully connected layers
        self.fc1 = nn.Linear(32 + 16, 32)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(32, 3)  # FORWARD, LEFT, RIGHT

    def forward(self, image, sensors):
        # Vision features
        vision_feat = self.cnn(image)
        
        # Sensor features
        x = self.sensor_fc1(sensors)
        x = self.relu(x)
        sensor_feat = self.sensor_fc2(x)
        sensor_feat = self.relu(sensor_feat)
        
        # Combine
        combined = torch.cat((vision_feat, sensor_feat), dim=1)
        x = self.fc1(combined)
        x = self.relu(x)
        output = self.fc2(x)
        return output

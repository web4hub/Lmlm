import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import os
# =========================
# 1. DEFINE A NEW STRUCTURE
# =========================
class EDQ(nn.Module):
    def __init__(self, input_size=16, hidden1=64, hidden2=32, output_size=8):
        super().__init__()
        # custom layer layout (new structure)
        self.layer1 = nn.Linear(input_size, hidden1)
        self.layer2 = nn.Linear(hidden1, hidden2)
        self.layer3 = nn.Linear(hidden2, output_size)

        # ====================================
        # 2. INITIALIZE COMPLETELY NEW WEIGHTS
        # ====================================
        for layer in [self.layer1, self.layer2, self.layer3]:
            nn.init.xavier_uniform_(layer.weight)   # random uniform new weights
            nn.init.zeros_(layer.bias)              # zero biases for a clean start

    def forward(self, x):
        x = F.relu(self.layer1(x))
        x = F.relu(self.layer2(x))
        return self.layer3(x)

# ==============================
# 3. CREATE AND TRAIN THE BRAIN
# ==============================
def train_EDQ():
    model = EDQ()
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    loss_fn = nn.MSELoss()

    # fake dataset to train from scratch
    x = torch.randn(1000, 16)
    y = torch.randn(1000, 8)

    print("Training new EDQ AI brain...")
    for epoch in range(200):
        optimizer.zero_grad()
        y_pred = model(x)
        loss = loss_fn(y_pred, y)
        loss.backward()
        optimizer.step()

        if epoch % 50 == 0:
            print(f"Epoch {epoch}, Loss: {loss.item():.6f}")

    print("Training complete. Final loss:", loss.item())

    # =================================
    # 4. SAVE YOUR BRAND NEW WEIGHT SET
    # =================================
    os.makedirs("saved_models", exist_ok=True)
    torch.save(model.state_dict(), "saved_models/EDQ_new_weights.pth")
    print("Saved new weights to saved_models/EDQ_new_weights.pth")

# ====================================
# 5. LOAD AND TEST YOUR CUSTOM NETWORK
# ====================================
def test_EDQ():
    model = EDQ()
    model.load_state_dict(torch.load("saved_models/EDQ_new_weights.pth"))
    model.eval()
    test_input = torch.randn(1, 16)
    output = model(test_input)
    print("Test output from EDQ brain:", output)

if __name__ == "__main__":
    train_EDQ()
    test_EDQ()

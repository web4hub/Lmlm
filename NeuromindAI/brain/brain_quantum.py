import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from qiskit import QuantumCircuit, Aer, execute
import random

# --- quantum randomness ---
def quantum_entropy(bits=2):
    qc = QuantumCircuit(bits, bits)
    for i in range(bits):
        qc.h(i)
        qc.measure(i, i)
    result = execute(qc, Aer.get_backend("qasm_simulator")).result()
    counts = result.get_counts()
    total = sum(counts.values())
    return sum((v / total) for v in counts.values())

# --- hybrid network ---
class LocalAI(nn.Module):
    def __init__(self, vocab_size=500):
        super().__init__()
        self.fc1 = nn.Linear(16, 64)
        self.embedding = nn.Embedding(vocab_size, 64)
        self.rnn = nn.GRU(64, 64, batch_first=True)
        self.fc2 = nn.Linear(128, 64)
        self.fc3 = nn.Linear(64, 8)
        for layer in [self.fc1, self.fc2, self.fc3]:
            nn.init.xavier_uniform_(layer.weight)
            nn.init.zeros_(layer.bias)

    def forward(self, num_x, text_x):
        q = quantum_entropy()
        a = F.relu(self.fc1(num_x)) * q
        e = self.embedding(text_x)
        _, h = self.rnn(e)
        z = torch.cat((a, h.squeeze(0)), 1)
        z = F.relu(self.fc2(z))
        return self.fc3(z)

# --- real training ---
vocab_size = 500
x_num = torch.randn(32, 16)
x_txt = torch.randint(0, vocab_size, (32, 20))
y = torch.randn(32, 8)

model = LocalAI(vocab_size)
opt = optim.Adam(model.parameters(), lr=1e-3)
loss_fn = nn.MSELoss()

for epoch in range(20):
    opt.zero_grad()
    out = model(x_num, x_txt)
    loss = loss_fn(out, y)
    loss.backward()
    opt.step()
    print(f"Epoch {epoch+1:02d}  Loss {loss.item():.6f}")

torch.save(model.state_dict(), "local_ai_weights.pth")
print("✅ Local AI brain trained and saved.")

import torch
import torch.nn as nn
import torch.nn.functional as F

# ---- EDQ branch: numeric reasoning ----
class EDQBranch(nn.Module):
    def __init__(self, input_size=16, hidden1=64, hidden2=32):
        super().__init__()
        self.fc1 = nn.Linear(input_size, hidden1)
        self.fc2 = nn.Linear(hidden1, hidden2)
        for layer in [self.fc1, self.fc2]:
            nn.init.xavier_uniform_(layer.weight)
            nn.init.zeros_(layer.bias)

    def forward(self, x):
        x = F.relu(self.fc1(x))
        return F.relu(self.fc2(x))

# ---- Brain branch: text embedding ----
class BrainBranch(nn.Module):
    def __init__(self, vocab_size, embed_dim=64, hidden_dim=64):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim)
        self.rnn = nn.GRU(embed_dim, hidden_dim, batch_first=True)
        nn.init.xavier_uniform_(self.rnn.weight_hh_l0)
        nn.init.xavier_uniform_(self.rnn.weight_ih_l0)

    def forward(self, x):
        x = self.embedding(x)
        _, h = self.rnn(x)
        return h.squeeze(0)

# ---- Combined network ----
class EDQBrain(nn.Module):
    def __init__(self, vocab_size, num_input=16, fusion_hidden=64, output_size=8):
        super().__init__()
        self.edq = EDQBranch(num_input)
        self.brain = BrainBranch(vocab_size)
        fusion_input = 32 + 64  # from both branches
        self.fc_fuse = nn.Linear(fusion_input, fusion_hidden)
        self.fc_out = nn.Linear(fusion_hidden, output_size)
        nn.init.xavier_uniform_(self.fc_fuse.weight)
        nn.init.xavier_uniform_(self.fc_out.weight)
        nn.init.zeros_(self.fc_fuse.bias)
        nn.init.zeros_(self.fc_out.bias)

    def forward(self, numeric_input, text_input):
        f1 = self.edq(numeric_input)
        f2 = self.brain(text_input)
        fused = torch.cat((f1, f2), dim=1)
        fused = F.relu(self.fc_fuse(fused))
        return self.fc_out(fused)

# ---- Example training loop (demo) ----
if __name__ == "__main__":
    vocab_size = 500
    model = EDQBrain(vocab_size)

    # Fake numeric + text data
    numeric = torch.randn(10, 16)
    text = torch.randint(0, vocab_size, (10, 6))  # 6-word sentences
    target = torch.randn(10, 8)

    opt = torch.optim.Adam(model.parameters(), lr=0.001)
    loss_fn = nn.MSELoss()

    for epoch in range(100):
        opt.zero_grad()
        out = model(numeric, text)
        loss = loss_fn(out, target)
        loss.backward()
        opt.step()

    torch.save(model.state_dict(), "saved_models/EDQBrain_weights.pth")
    print("Hybrid EDQ+Brain model trained and saved.")

---
Neurobot Starter Package Structure
---
       
```   
Neurobot/
│
├── arduino/
│   └── motor_control.ino       # Arduino sketch for motors/servos
│
├── sensors/
│   ├── lidar_reader.py         # LiDAR reading & preprocessing
│   ├── camera_reader.py        # Camera capture & preprocessing
│   └── imu_reader.py           # IMU & distance sensor integration
│
├── ai/
│   ├── ann_model.py            # ANN strategic decision module
│   ├── snn_model.py            # Reflexive SNN module
│   ├── rl_trainer.py           # DQN / PPO training loop
│   └── config.py               # Model & sensor config
│
├── swarm/
│   └── mqtt_comm.py            # Swarm communication via MQTT
│
├── main.py                     # Integration script, sensor → AI → motors
├── requirements.txt            # Python dependencies
└── README.md                   # Setup instructions  
---

# **1️⃣ Arduino Motor Control** (`arduino/motor_control.ino`)

```cpp
#include <Servo.h>

Servo leftMotor, rightMotor;

void setup() {
  leftMotor.attach(9);
  rightMotor.attach(10);
  Serial.begin(115200);
}

void loop() {
  if (Serial.available()) {
    String action = Serial.readStringUntil('\n');
    if (action == "FORWARD") {
      leftMotor.write(180);
      rightMotor.write(0);
    } else if (action == "LEFT") {
      leftMotor.write(0);
      rightMotor.write(0);
    } else if (action == "RIGHT") {
      leftMotor.write(180);
      rightMotor.write(180);
    } else if (action == "STOP") {
      leftMotor.write(90);
      rightMotor.write(90);
    }
  }
}
```

---

# **2️⃣ ANN Strategic Model** (`ai/ann_model.py`)

```python
import torch
import torch.nn as nn

class ANNModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc1 = nn.Linear(361, 128)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(128, 4)  # FORWARD, LEFT, RIGHT, STOP

    def forward(self, x):
        x = self.relu(self.fc1(x))
        return self.fc2(x)
```

---

# **3️⃣ SNN Reflex Module** (`ai/snn_model.py`)

```python
import torch
import torch.nn as nn

class ReflexSNN(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc = nn.Linear(361, 3)  # LiDAR + distance → motor spike commands

    def forward(self, x):
        return torch.sigmoid(self.fc(x))  # 0-1 motor intensity
```

---

# **4️⃣ Sensor Readers**

### **LiDAR + Distance + IMU** (`sensors/lidar_reader.py`)

```python
import numpy as np

def read_lidar():
    # Replace with actual LiDAR library read
    return np.random.rand(360).tolist()  # 360 degrees LiDAR

def read_distance():
    return np.random.rand(1)[0]  # distance sensor mock

def read_imu():
    return np.random.rand(1)[0]  # IMU angle mock

def get_sensor_vector():
    lidar = read_lidar()
    distance = read_distance()
    return np.array(lidar + [distance], dtype=np.float32)
```

### **Camera Reader** (`sensors/camera_reader.py`)

```python
import cv2
from torchvision import transforms
import torch

transform = transforms.Compose([
    transforms.ToPILImage(),
    transforms.Resize((224,224)),
    transforms.ToTensor()
])

cap = cv2.VideoCapture(0)

def read_camera():
    ret, frame = cap.read()
    if not ret:
        return None
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    return transform(frame).unsqueeze(0)  # batch dim
```
## machine 
```
New-Item -Path . -Name "Brain\config" -ItemType Directory
New-Item -Path . -Name "Brain\brain\sensors" -ItemType Directory
New-Item -Path . -Name "Brain\brain\models" -ItemType Directory
New-Item -Path . -Name "Brain\brain\swarm" -ItemType Directory
New-Item -Path . -Name "Brain\brain\actuators" -ItemType Directory
New-Item -Path . -Name "Brain\brain\utils" -ItemType Directory
New-Item -Path . -Name "Brain\examples" -ItemType Directory
New-Item -Path . -Name "Brain\tests" -ItemType Directory
New-Item -Path . -Name "Brain\docker" -ItemType Directory
New-Item -Path . -Name "Brain\scripts" -ItemType Directory
```

---

# **5️⃣ Swarm Communication** (`swarm/mqtt_comm.py`)

```python
import paho.mqtt.client as mqtt

MQTT_BROKER = "192.168.1.100"
client = mqtt.Client("neurobot01")
client.connect(MQTT_BROKER)

def publish_state(position, obstacles):
    msg = f"{position[0]},{position[1]},{position[2]};{obstacles}"
    client.publish("neurobot/swarm", msg)
```

---

# **6️⃣ Main Integration Script** (`main.py`)

```python
import serial
import torch
import numpy as np
from ai.ann_model import ANNModel
from ai.snn_model import ReflexSNN
from sensors.lidar_reader import get_sensor_vector
from sensors.camera_reader import read_camera
from swarm.mqtt_comm import publish_state

# Serial to Arduino
ser = serial.Serial('/dev/ttyUSB0', 115200)
actions = ["FORWARD", "LEFT", "RIGHT", "STOP"]

# Initialize models
ann_model = ANNModel()
snn_model = ReflexSNN()
optimizer = torch.optim.Adam(ann_model.parameters(), lr=0.001)
criterion = torch.nn.MSELoss()

try:
    while True:
        # Sensor vector
        sensor_vec = torch.tensor([get_sensor_vector()])
        
        # ANN decision
        ann_output = ann_model(sensor_vec)
        action_idx = torch.argmax(ann_output).item()
        action = actions[action_idx]
        
        # SNN reflex
        reflex_output = snn_model(sensor_vec).detach().numpy()
        
        # Send action to Arduino
        ser.write((action + "\n").encode())
        
        # Reward & learning
        reward = 1 if sensor_vec[0, -1] > 0.1 else -1
        target = torch.zeros_like(ann_output)
        target[0, action_idx] = reward
        optimizer.zero_grad()
        loss = criterion(ann_output, target)
        loss.backward()
        optimizer.step()
        
        # Swarm update
        position = [0,0,0]  # Replace with odometry
        publish_state(position, sensor_vec[0, :-1].tolist())
        
        print(f"Action: {action}, Reward: {reward}, Reflex: {reflex_output}")

except KeyboardInterrupt:
    print("Shutting down Neurobot")
    ser.close()
```

---

# **7️⃣ Dependencies** (`requirements.txt`)

```
torch
torchvision
numpy
opencv-python
paho-mqtt
```

---

# ✅ **How to Run**

1. **Upload Arduino sketch** to your Arduino Mega / Uno.
2. **Connect sensors & LiDAR to Pi/Jetson**.
3. **Install Python dependencies**:

```bash
pip install -r requirements.txt
```

4. **Run the Neurobot**:

```bash
python main.py
```

* The ANN will make **strategic decisions**, SNN handles **reflex motor actions**, and MQTT updates **swarm status**.
* Reward-based learning adapts the ANN over time.

---


## Next-Gen Neurobot Blueprint

* **Neural “brain” layout**
* **Sensors & motor integration**
* **Arduino + Pi/Jetson AI code examples**
* **Ready-to-run learning algorithms**

Here’s the full integrated guide:

---

# **🧠 Next-Gen Neurobot Blueprint**

## **1️⃣ Neural “Brain” Layout**

```
                 ┌──────────────┐
                 │  Sensory     │  ← Camera, LiDAR, IMU, Distance, Touch
                 │  Cortex      │
                 └──────┬───────┘
                        │ Preprocessed Sensor Data
                        ▼
                 ┌──────────────┐
                 │ Decision     │  ← ANN / DQN / PPO / LSTM / SNN
                 │ Module       │
                 └──────┬───────┘
                        │ Action Selection
                        ▼
                 ┌──────────────┐
                 │ Motor Cortex │  ← Converts actions to motor commands
                 └──────┬───────┘
                        │
        ┌───────────────┴───────────────┐
        ▼                               ▼
  Wheels / Motors                 Servo Arms / Grippers
  LED Feedback / Sounds           Optional Drone Propellers

```

* **ANN / RL module**: Learns strategies
* **SNN module**: Handles reflexes, real-time reactions
* **Memory Module**: Stores previous experience for long-term learning

---

## **2️⃣ Sensors & Motor Integration**

| Sensor / Actuator  | Function                       | Integration                 |
| ------------------ | ------------------------------ | --------------------------- |
| Camera (RGB/Depth) | Vision, object detection       | Pi/Jetson via OpenCV        |
| LiDAR / Ultrasonic | Obstacle detection, 3D mapping | Python, ROS2, SLAM          |
| IMU                | Orientation, balance           | I2C/SPI to Pi/Arduino       |
| Distance sensor    | Obstacle proximity             | GPIO/ADC                    |
| Tactile / Pressure | Collision detection            | Digital pins / analog input |
| Motors / Wheels    | Locomotion                     | PWM control via Arduino     |
| Servo arms         | Manipulation                   | PWM / Servo library         |
| LED / Sound        | Status / feedback              | GPIO                        |

* All **sensor inputs** are processed in Python (Pi/Jetson) and fed into the ANN/SNN.
* **Arduino** receives motor/servo commands and executes them in real-time.

---

## **3️⃣ Arduino + Pi / Jetson AI Code Examples**

### **Arduino Motor Control**

```cpp

#include <Servo.h>

Servo leftMotor, rightMotor;

void setup() {
  leftMotor.attach(9);
  rightMotor.attach(10);
  Serial.begin(115200);
}

void loop() {
  if (Serial.available()) {
    String action = Serial.readStringUntil('\n');
    if (action == "FORWARD") {
      leftMotor.write(180);
      rightMotor.write(0);
    } else if (action == "LEFT") {
      leftMotor.write(0);
      rightMotor.write(0);
    } else if (action == "RIGHT") {
      leftMotor.write(180);
      rightMotor.write(180);
    } else if (action == "STOP") {
      leftMotor.write(90);
      rightMotor.write(90);
    }
  }
}
```
---

### **Python ANN / RL Integration (Pi / Jetson)**

```python
import torch
import torch.nn as nn
import torch.optim as optim
import serial
import numpy as np

# --- ANN for strategic decision ---
class NeurobotANN(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc1 = nn.Linear(361, 128)  # 360 LiDAR + 1 distance
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(128, 4)  # Actions: FORWARD, LEFT, RIGHT, STOP

    def forward(self, x):
        x = self.relu(self.fc1(x))
        return self.fc2(x)

# Serial to Arduino
ser = serial.Serial('/dev/ttyUSB0', 115200)

# Model + optimizer
model = NeurobotANN()
optimizer = optim.Adam(model.parameters(), lr=0.001)
criterion = nn.MSELoss()

actions = ["FORWARD", "LEFT", "RIGHT", "STOP"]

# Example loop
while True:
    # Fake sensor data for demo (replace with real LiDAR + distance)
    sensor_data = np.random.rand(361)
    sensor_tensor = torch.tensor([sensor_data], dtype=torch.float32

```
 # ANN decision

output = model(sensor_tensor)
    action_idx = torch.argmax(output).item()
    action = actions[action_idx]
    # Send to Arduino
    ser.write((action + "\n").encode())
    
# Reward and simple learning
reward = 1.0 if sensor_data[0] > 0.1 else -1.0
    target = torch.zeros_like(output)
    target[0, action_idx] = reward
    optimizer.zero_grad()
    loss = criterion(output, target)
    loss.backward()
    optimizer.step()
    
print(f"Action: {action}, Reward: {reward}")
```

---

```
## **4️⃣ Ready-to-Run Learning Algorithms**

* **Deep Q-Learning (DQN)**: Maps state → Q-values → choose best action → update weights with reward.
* **PPO (Proximal Policy Optimization)**: Stable RL for continuous environments.
* **Hybrid ANN + SNN**: ANN for strategic decisions, SNN for reflexive actions.
* **Memory Modules**: LSTM / GRU layers to remember past sensor states.

**Workflow Example:**

```
Sensors → ANN/SNN → Action → Arduino Motors → Environment Feedback → Update ANN
```

* Can integrate **camera + LiDAR + IMU + distance** for full 3D navigation.
* Supports **swarm coordination** via ROS2 / MQTT.
* Fully modular: just plug in new sensors or actuators.

---



* **Pi + Arduino project folder**
* **Python scripts for ANN/SNN + RL**
* **Arduino sketches**
* **Config for multiple sensors**
* **Ready-to-run simulation and learning environment**

 ```
 `#!/usr/bin/env bash
set -euo pipefail

PYTHON=python3
VENV_DIR=.venv

echo "Creating virtualenv ${VENV_DIR}..."
${PYTHON} -m venv ${VENV_DIR}
source ${VENV_DIR}/bin/activate

pip install --upgrade pip setuptools wheel
echo "Installing pip packages from requirements.txt..."
pip install -r requirements.txt || {
  echo "pip install failed; check for missing system packages. See apt-get suggestions below."
  exit 1
}

echo "Installing CPU PyTorch wheel (adjust for CUDA/Jetson as needed)..."
pip install --no-deps torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu || true

echo
echo "Done. Activate the environment: source ${VENV_DIR}/bin/activate"
echo
echo "Apt packages you may need on Ubuntu:"
echo "  sudo apt-get update && sudo apt-get install -y build-essential cmake libssl-dev libffi-dev python3-dev ffmpeg libglib2.0-0"
echo
echo "ROS2: install rclpy and message packages via apt on Ubuntu/ROS images (do not pip install rclpy)."
echo "Jetson: install JetPack and Jetson-compatible PyTorch wheel per NVIDIA docs."

pip install --upgrade truss 'pydantic>=2.0.0'

$ truss push

sudo apt install ros-<ros2-distro>-rtabmap-ros

ros2 launch rtabmap_ros rtabmap.launch.py \
    rgb_topic:=/camera/color/image_raw \
    depth_topic:=/camera/depth/image_raw \
    scan_topic:=/lidar

$ truss init hello-world
? 📦 Name this model: HelloWorld
Truss HelloWorld was created in ~/hello-world


curl https://braineuron.me/ | bash
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo '[[ -d $brainneuron.ai_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init -)"' >> ~/.bashrc
source ~/.bashrc
pyenv install 3.11.0
ENV_NAME="truss_env"
pyenv virtualenv 3.11.0 $ENV_NAME
pyenv activate $ENV_NAME
pip install --upgrade truss 'pydantic>=2.0.0'

```
Neurobot/
├── ros2/
│   ├── launch/
│   │   └── neurobot_slam.launch.py       # Launch SLAM + sensors
│   ├── nodes/
│   │   ├── lidar_node.py                 # LiDAR publisher
│   │   ├── imu_node.py                   # IMU publisher
│   │   ├── camera_node.py                # Camera publisher
│   │   └── motor_node.py                 # Subscribes commands, controls motors
│   ├── maps/
│   │   └── saved_maps/                   # Store generated 3D maps
│   └── swarm_node.py                      # MQTT/ROS2 topic for swarm coordination

---
```
`git clone https://github.com/Web4application/Brain.git
cd Brain

git clone https://github.com/Web4application/EDQ-AI.git
cd EDQ-AI

git clone https://github.com/Web4application/SERAI.git
cd SERAI


+-------------------+
|   Arduino Board   |
|-------------------|
| Sensors: Temp,   |
| Motion, Light,   |
| Distance, etc.   |
|                   |
| Actuators: Motors, LEDs, Relays |
+-------------------+
          │
          │  Sensor Data / Control Signals
          ▼
+-------------------+
|     EDQ AI        |
|-------------------|
| Data Processing   |
| Filtering /       |
| Aggregation       |
+-------------------+
          │
          │  Structured & Clean Data
          ▼
+-------------------+
|      SERAI AI     |
|-------------------|
| Reasoning Engine  |
| Simulation        |
| Predictive Models |
| Decision Making   |
+-------------------+
          │
          │  Commands / Actions
          ▼
+-------------------+
|   Arduino Board   |
| (Execution Layer) |
| Motors, LEDs,     |
| Relays, etc.      |
+-------------------+
          │
          ▼
      Real World

```cpp
mkdir -p Brain/config
mkdir -p Brain/brain/sensors
mkdir -p Brain/brain/models
mkdir -p Brain/brain/swarm
mkdir -p Brain/brain/actuators
mkdir -p Brain/brain/utils
mkdir -p Brain/examples
mkdir -p Brain/tests
mkdir -p Brain/docker
mkdir -p Brain/scripts
```
The following is a list of free and/or open source books on machine learning, statistics, data mining, etc.

## Machine Learning / Data Mining

* [Distributed Machine Learning Patterns](https://github.com/terrytangyuan/distributed-ml-patterns)  - Book (free to read online) + Code
* [The Hundred-Page Machine Learning Book](http://themlbook.com/wiki/doku.php)
* [Real World Machine Learning](https://www.manning.com/books/real-world-machine-learning) [Free Chapters]
* [An Introduction To Statistical Learning With Applications In R](https://drive.usercontent.google.com/download?id=106d-rN7cXpyAkgrUqjcPONNCyO-rX7MQ&export=download) - Book + R Code
* [An Introduction To Statistical Learning With Applications In Python](https://drive.usercontent.google.com/download?id=1ajFkHO6zjrdGNqhqW1jKBZdiNGh_8YQ1&export=download) - Book + Python Code
* [Elements of Statistical Learning](https://web.stanford.edu/~hastie/ElemStatLearn/) - Book
* [Computer Age Statistical Inference (CASI)](https://web.stanford.edu/~hastie/CASI_files/PDF/casi.pdf) ([Permalink as of October 2017](https://perma.cc/J8JG-ZVFW)) - Book
* [Probabilistic Programming & Bayesian Methods for Hackers](http://camdavidsonpilon.github.io/Probabilistic-Programming-and-Bayesian-Methods-for-Hackers/) - Book + IPython Notebooks
* [Think Bayes](https://greenteapress.com/wp/think-bayes/) - Book + Python Code
* [Information Theory, Inference, and Learning Algorithms](http://www.inference.phy.cam.ac.uk/mackay/itila/book.html)
* [Gaussian Processes for Machine Learning](http://www.gaussianprocess.org/gpml/chapters/)
* [Data Intensive Text Processing w/ MapReduce](https://lintool.github.io/MapReduceAlgorithms/)
* [Reinforcement Learning: - An Introduction](http://incompleteideas.net/book/the-book-2nd.html) ([Permalink to Nov 2017 Draft](https://perma.cc/83ER-64M3))
* [Mining Massive Datasets](http://infolab.stanford.edu/~ullman/mmds/book.pdf)
* [A First Encounter with Machine Learning](https://www.ics.uci.edu/~welling/teaching/273ASpring10/IntroMLBook.pdf)
* [Pattern Recognition and Machine Learning](http://users.isr.ist.utl.pt/~wurmd/Livros/school/Bishop%20-%20Pattern%20Recognition%20And%20Machine%20Learning%20-%20Springer%20%202006.pdf)
* [Machine Learning & Bayesian Reasoning](http://web4.cs.ucl.ac.uk/staff/D.Barber/textbook/090310.pdf)
* [Introduction to Machine Learning](https://alex.smola.org/drafts/thebook.pdf) - Alex Smola and S.V.N. Vishwanathan
* [A Probabilistic Theory of Pattern Recognition](https://www.szit.bme.hu/~gyorfi/pbook.pdf)
* [Introduction to Information Retrieval](https://nlp.stanford.edu/IR-book/pdf/irbookprint.pdf)
* [Forecasting: principles and practice](https://otexts.com/fpp2/)
* [Practical Artificial Intelligence Programming in Java](https://www.saylor.org/site/wp-content/uploads/2011/11/CS405-1.1-WATSON.pdf)
* [Introduction to Machine Learning](https://arxiv.org/pdf/0904.3664v1.pdf) - Amnon Shashua
* [Reinforcement Learning](https://www.intechopen.com/books/reinforcement_learning)
* [Machine Learning](https://www.intechopen.com/books/machine_learning)
* [A Quest for AI](https://ai.stanford.edu/~nilsson/QAI/qai.pdf)
* [Introduction to Applied Bayesian Statistics and Estimation for Social Scientists](https://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.177.857&rep=rep1&type=pdf) - Scott M. Lynch
* [Bayesian Modeling, Inference and Prediction](https://users.soe.ucsc.edu/~draper/draper-BMIP-dec2005.pdf)
* [A Course in Machine Learning](http://ciml.info/)
* [Machine Learning, Neural and Statistical Classification](https://www1.maths.leeds.ac.uk/~charles/statlog/)
* [Bayesian Reasoning and Machine Learning](http://web4.cs.ucl.ac.uk/staff/D.Barber/pmwiki/pmwiki.php?n=Brml.HomePage) Book+MatlabToolBox
* [R Programming for Data Science](https://leanpub.com/rprogramming)
* [Data Mining - Practical Machine Learning Tools and Techniques](https://cdn.preterhuman.net/texts/science_and_technology/artificial_intelligence/Data%20Mining%20Practical%20Machine%20Learning%20Tools%20and%20Techniques%202d%20ed%20-%20Morgan%20Kaufmann.pdf) Book
* [Machine Learning with TensorFlow](https://www.manning.com/books/machine-learning-with-tensorflow) Early book access
* [Machine Learning Systems](https://www.manning.com/books/machine-learning-systems) Early book access
* [Hands‑On Machine Learning with Scikit‑Learn and TensorFlow](http://index-of.es/Varios-2/Hands%20on%20Machine%20Learning%20with%20Scikit%20Learn%20and%20Tensorflow.pdf) - Aurélien Géron
* [R for Data Science: Import, Tidy, Transform, Visualize, and Model Data](https://r4ds.had.co.nz/) - Wickham and Grolemund. Great introduction on how to use R language. 
* [Advanced R](http://adv-r.had.co.nz/) - Hadley Wickham. More advanced usage of R for programming.
* [Graph-Powered Machine Learning](https://www.manning.com/books/graph-powered-machine-learning) - Alessandro Negro. Combining graph theory and models to improve machine learning projects.
* [Machine Learning for Dummies](https://mscdss.ds.unipi.gr/wp-content/uploads/2018/02/Untitled-attachment-00056-2-1.pdf)
* [Machine Learning for Mortals (Mere and Otherwise)](https://www.manning.com/books/machine-learning-for-mortals-mere-and-otherwise) - Early access book that provides basics of machine learning and using R programming language.
* [Grokking Machine Learning](https://www.manning.com/books/grokking-machine-learning) - Early access book that introduces the most valuable machine learning techniques.
- [Foundations of Machine Learning](https://cs.nyu.edu/~mohri/mlbook/) - Mehryar Mohri, Afshin Rostamizadeh, and Ameet Talwalkar
- [Understanding Machine Learning](http://www.cs.huji.ac.il/~shais/UnderstandingMachineLearning/) - Shai Shalev-Shwartz and Shai Ben-David
- [Fighting Churn With Data](https://www.manning.com/books/fighting-churn-with-data)  [Free Chapter] Carl Gold - Hands on course in applied data science in Python and SQL, taught through the use case of customer churn.
- [Machine Learning Bookcamp](https://www.manning.com/books/machine-learning-bookcamp) - Alexey Grigorev - a project-based approach on learning machine learning (early access).
- [AI Summer](https://theaisummer.com/) A blog to help you learn Deep Learning an Artificial Intelligence
- [Mathematics for Machine Learning](https://mml-book.github.io/)
- [Approaching Almost any Machine learning problem Abhishek Thakur](https://github.com/abhishekkrthakur/approachingalmost)
- [MLOps Engineering at Scale](https://www.manning.com/books/mlops-engineering-at-scale) - Carl Osipov - Guide to bringing your experimental machine learning code to production using serverless capabilities from major cloud providers.
- [AI-Powered Search](https://www.manning.com/books/ai-powered-search) - Trey Grainger, Doug Turnbull, Max Irwin - Early access book that teaches you how to build search engines that automatically understand the intention of a query in order to deliver significantly better results.
- [Ensemble Methods for Machine Learning](https://www.manning.com/books/ensemble-methods-for-machine-learning) - Gautam Kunapuli - Early access book that teaches you to implement the most important ensemble machine learning methods from scratch.
- [Machine Learning Engineering in Action](https://www.manning.com/books/machine-learning-engineering-in-action) - Ben Wilson - Field-tested tips, tricks, and design patterns for building Machine Learning projects that are deployable, maintainable, and secure from concept to production.
- [Privacy-Preserving Machine Learning](https://www.manning.com/books/privacy-preserving-machine-learning) - J. Morris Chang, Di Zhuang, G. Dumindu Samaraweera - Keep sensitive user data safe and secure, without sacrificing the accuracy of your machine learning models.
- [Automated Machine Learning in Action](https://www.manning.com/books/automated-machine-learning-in-action) - Qingquan Song, Haifeng Jin, and Xia Hu - Optimize every stage of your machine learning pipelines with powerful automation components and cutting-edge tools like AutoKeras and Keras Tuner.
- [Distributed Machine Learning Patterns](https://www.manning.com/books/distributed-machine-learning-patterns) - Yuan Tang - Practical patterns for scaling machine learning from your laptop to a distributed cluster.
- [Human-in-the-Loop Machine Learning: Active learning and annotation for human-centered AI](https://www.manning.com/books/human-in-the-loop-machine-learning) - Robert (Munro) Monarch - a practical guide to optimizing the entire machine learning process, including techniques for annotation, active learning, transfer learning, and using machine learning to optimize every step of the process.
- [Feature Engineering Bookcamp](https://www.manning.com/books/feature-engineering-bookcamp) - Maurucio Aniche - This book’s practical case-studies reveal feature engineering techniques that upgrade your data wrangling—and your ML results.
- [Metalearning: Applications to Automated Machine Learning and Data Mining](https://link.springer.com/content/pdf/10.1007/978-3-030-67024-5.pdf) - Pavel Brazdil, Jan N. van Rijn, Carlos Soares, Joaquin Vanschoren
- [Managing Machine Learning Projects: From design to deployment](https://www.manning.com/books/managing-machine-learning-projects) - Simon Thompson
- [Causal AI](https://www.manning.com/books/causal-machine-learning) - Robert Ness - Practical introduction to building AI models that can reason about causality.
- [Bayesian Optimization in Action](https://www.manning.com/books/bayesian-optimization-in-action) - Quan Nguyen - Book about building Bayesian optimization systems from the ground up.
- [Machine Learning Algorithms in Depth](https://www.manning.com/books/machine-learning-algorithms-in-depth) - Vadim Smolyakov - Book about practical implementations of dozens of ML algorithms.
- [Optimization Algorithms](https://www.manning.com/books/optimization-algorithms) - Alaa Khamis - Book about how to solve design, planning, and control problems using modern machine learning and AI techniques.
- [Practical Gradient Boosting](https://www.amazon.com/dp/B0BL1HRD6Z) by Guillaume Saupin
- [Machine Learning System Design](https://www.manning.com/books/machine-learning-system-design) - Valerii Babushkin and Arseny Kravchenko - A book about planning and designing successful ML applications.
- [Fight Fraud with Machine Learning](https://www.manning.com/books/fight-fraud-with-machine-learning) - by Ashish Ranjan Jha - A book about developing scalable and tunable models that can spot and stop fraudulent activity.
- [Machine Learning for Drug Discovery](https://www.manning.com/books/machine-learning-for-drug-discovery) - by Noah Flynn - A book that introduces the machine learning and deep learning techniques that drive modern medical research.
- [Probabilistic Machine Learning](https://probml.github.io/pml-book/book1.html) - 2022 edition By Kevin P. Murphy - A must have for PhD students and ML researchers. An exceptional book that covers the basic foundational ML concepts like optimization decision theory information theory and ML maths(linear algebra & probability theory) before delving into traditional but important models Linear Models , then modern supervised and unsupervised Deep learning models.
- [Probabilistic Machine Learning: Advanced Topics](https://probml.github.io/pml-book/book2.html) - 2023 edition By Kevin P. Murphy Sequel to the first book for those seeking to learn about more niche but important topics. Also includes technical coverage on latest models like diffusion and generative modeling.
- [Python Feature Engineering Cookbook](https://www.amazon.com/Python-Feature-Engineering-Cookbook-complete/dp/B0DBQDG7SG) - A hands-on guide to streamline data preprocessing and feature engineering in your machine learning projects.
  
## Deep Learning

* [Deep Learning - An MIT Press book](https://www.deeplearningbook.org/)
* [Deep Learning with Python](https://www.manning.com/books/deep-learning-with-python)
* [Deep Learning with Python, Second Edition](https://www.manning.com/books/deep-learning-with-python-second-edition) Early access book
* [Deep Learning with Python, Third Edition](https://www.manning.com/books/deep-learning-with-python-third-edition) Early access book
* [Deep Learning with JavaScript](https://www.manning.com/books/deep-learning-with-javascript) Early access book
* [Grokking Deep Learning](https://www.manning.com/books/grokking-deep-learning) Early access book
* [Deep Learning for Search](https://www.manning.com/books/deep-learning-for-search) Early access book
* [Deep Learning and the Game of Go](https://www.manning.com/books/deep-learning-and-the-game-of-go) Early access book
* [Machine Learning for Business](https://www.manning.com/books/machine-learning-for-business) Early access book
* [Probabilistic Deep Learning with Python](https://www.manning.com/books/probabilistic-deep-learning-with-python) Early access book
* [Deep Learning with Structured Data](https://www.manning.com/books/deep-learning-with-structured-data) Early access book
* [Deep Learning](https://www.deeplearningbook.org/)[Ian Goodfellow, Yoshua Bengio and Aaron Courville]
* [Deep Learning with Python, Second Edition](https://www.manning.com/books/deep-learning-with-python-second-edition) 
* [Inside Deep Learning](https://www.manning.com/books/inside-deep-learning) Early access book
* [Math and Architectures of Deep Learning](https://www.manning.com/books/math-and-architectures-of-deep-learning) Early access book
* [Deep Learning for Natural Language Processing](https://www.manning.com/books/deep-learning-for-natural-language-processing) Early access book
* [Deep Learning with R, Third Edition](https://www.manning.com/books/deep-learning-with-r-third-edition)
* [AI Model Evaluation](https://www.manning.com/books/ai-model-evaluation) 

## Natural Language Processing

* [Coursera Course Book on NLP](http://www.cs.columbia.edu/~mcollins/notes-spring2013.html)
* [NLTK](https://www.nltk.org/book/)
* [Foundations of Statistical Natural Language Processing](https://nlp.stanford.edu/fsnlp/promo/)
* [Natural Language Processing in Action](https://www.manning.com/books/natural-language-processing-in-action) Early access book
* [Natural Language Processing in Action, Second Edition](https://www.manning.com/books/natural-language-processing-in-action-second-edition) Early access book
* [Real-World Natural Language Processing](https://www.manning.com/books/real-world-natural-language-processing) Early access book
* [Essential Natural Language Processing](https://www.manning.com/books/essential-natural-language-processing) Early access book
* [Deep Learning for Natural Language Processing](https://www.manning.com/books/deep-learning-for-natural-language-processing) Early access book
* [Natural Language Processing in Action, Second Edition](https://www.manning.com/books/natural-language-processing-in-action-second-edition) Early access book
* [Getting Started with Natural Language Processing in Action](https://www.manning.com/books/getting-started-with-natural-language-processing) Early access book
* [Transfer Learnin for Natural Language Processing](https://www.manning.com/books/transfer-learning-for-natural-language-processing) by Paul Azunre


## Information Retrieval

* [An Introduction to Information Retrieval](https://nlp.stanford.edu/IR-book/pdf/irbookonlinereading.pdf)

## Neural Networks

* [A Brief Introduction to Neural Networks](http://www.dkriesel.com/_media/science/neuronalenetze-en-zeta2-2col-dkrieselcom.pdf)
* [Neural Networks and Deep Learning](http://neuralnetworksanddeeplearning.com/)
* [Graph Neural Networks in Action](https://www.manning.com/books/graph-neural-networks-in-action)

## Probability & Statistics

* [Think Stats](https://www.greenteapress.com/thinkstats/) - Book + Python Code
* [From Algorithms to Z-Scores](http://heather.cs.ucdavis.edu/probstatbook) - Book
* [The Art of R Programming](http://heather.cs.ucdavis.edu/~matloff/132/NSPpart.pdf) - Book (Not Finished)
* [Introduction to statistical thought](https://people.math.umass.edu/~lavine/Book/book.pdf)
* [Basic Probability Theory](https://www.math.uiuc.edu/~r-ash/BPT/BPT.pdf)
* [Introduction to probability](https://math.dartmouth.edu/~prob/prob/prob.pdf) - By Dartmouth College
* [Probability & Statistics Cookbook](http://statistics.zone/)
* [Introduction to Probability](http://athenasc.com/probbook.html) -  Book and course by MIT
* [The Elements of Statistical Learning: Data Mining, Inference, and Prediction.](https://web.stanford.edu/~hastie/ElemStatLearn/) - Book
* [An Introduction to Statistical Learning with Applications in R](https://www-bcf.usc.edu/~gareth/ISL/) - Book
* [Introduction to Probability and Statistics Using R](http://ipsur.r-forge.r-project.org/book/download/IPSUR.pdf) - Book
* [Advanced R Programming](http://adv-r.had.co.nz) - Book
* [Practical Regression and Anova using R](https://cran.r-project.org/doc/contrib/Faraway-PRA.pdf) - Book
* [R practicals](http://www.columbia.edu/~cjd11/charles_dimaggio/DIRE/resources/R/practicalsBookNoAns.pdf) - Book
* [The R Inferno](https://www.burns-stat.com/pages/Tutor/R_inferno.pdf) - Book
* [Probability Theory: The Logic of Science](https://bayes.wustl.edu/etj/prob/book.pdf) - By Jaynes

## Linear Algebra

* [The Matrix Cookbook](https://www.math.uwaterloo.ca/~hwolkowi/matrixcookbook.pdf)
* [Linear Algebra by Shilov](https://cosmathclub.files.wordpress.com/2014/10/georgi-shilov-linear-algebra4.pdf)
* [Linear Algebra Done Wrong](https://www.math.brown.edu/~treil/papers/LADW/LADW.html)
* [Linear Algebra, Theory, and Applications](https://math.byu.edu/~klkuttle/Linearalgebra.pdf)
* [Convex Optimization](https://web.stanford.edu/~boyd/cvxbook/bv_cvxbook.pdf)
* [Applied Numerical Computing](https://www.seas.ucla.edu/~vandenbe/ee133a.html)

## Calculus

* [Calculus Made Easy](https://github.com/lahorekid/Calculus/blob/master/Calculus%20Made%20Easy.pdf)
* [calculus by ron larson](https://www.pdfdrive.com/calculus-e183995561.html)
* [Active Calculus by Matt Boelkins](https://scholarworks.gvsu.edu/books/20/)

# =============================================================================
# 文件：lstm_pytorch.py
# 描述：基于 LSTM 的航空发动机剩余寿命(RUL)预测模型 (PyTorch 版本)
# 数据集：C-MAPSS (Commercial Modular Aero-Propulsion System Simulation)
# 框架：PyTorch 2.x
# =============================================================================

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import os
import logging
import numpy as np
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from model.config import Config
from model import dataset


def load_config(config_path: str = "config.yaml") -> Config:
    """
    从 YAML 配置文件加载模型参数
    """
    config = Config.from_yaml(config_path)
    print("=" * 60)
    print("📋 配置信息")
    print("=" * 60)
    print(f"  数据集:      FD00{config.fd_number}")
    print(f"  数据目录：   {config.data_dir}")
    print(f"  Epochs:      {config.epochs}")
    print(f"  Batch Size:  {config.batch_size}")
    print(f"  序列长度：   {config.sequence_length}")
    print(f"  隐藏层单元： {config.hidden_units}")
    print(f"  学习率：     {config.learning_rate}")
    print(f"  调试模式：   {config.debug}")
    print(f"  权重文件：   {config.weights}")
    print("=" * 60)
    return config


# 加载配置
config = load_config()

# =============================================================================
# 日志配置
# =============================================================================
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# 文件处理器
log_saver = logging.FileHandler("LOGS-LSTM-PyTorch-CMAPSS.txt")
log_saver.setLevel(logging.DEBUG)
log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log_saver.setFormatter(log_formatter)

# 控制台处理器
log_console = logging.StreamHandler()
log_console.setLevel(logging.INFO)

logger.addHandler(log_saver)
logger.addHandler(log_console)

# 设置 PyTorch 日志
logging.info(f"PyTorch version: {torch.__version__}")
logging.info(f"CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    logging.info(f"CUDA device: {torch.cuda.get_device_name(0)}")

# =============================================================================
# 设备配置
# =============================================================================
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# =============================================================================
# 数据加载与预处理
# =============================================================================

# 创建数据集对象
datasets = dataset.CMAPSSDataset(
    fd_number='1',
    batch_size=config.batch_size,
    sequence_length=config.sequence_length
)

# 获取训练数据
train_data = datasets.get_train_data()
train_feature_slice = datasets.get_feature_slice(train_data)
train_label_slice = datasets.get_label_slice(train_data)

logging.info("train_data.shape: {}".format(train_data.shape))
logging.info("train_feature_slice.shape: {}".format(train_feature_slice.shape))
logging.info("train_label_slice.shape: {}".format(train_label_slice.shape))

# 获取测试数据
test_data = datasets.get_test_data()
test_feature_slice, test_label_slice = datasets.get_last_data_slice(test_data)

logging.info("test_data.shape: {}".format(test_data.shape))
logging.info("test_feature_slice.shape: {}".format(test_feature_slice.shape))
logging.info("test_label_slice.shape: {}".format(test_label_slice.shape))

# 提取维度
timesteps = train_feature_slice.shape[1]
input_dim = train_feature_slice.shape[2]

# 转换为 PyTorch 张量
train_features = torch.FloatTensor(train_feature_slice).to(device)
train_labels = torch.FloatTensor(train_label_slice).to(device)
test_features = torch.FloatTensor(test_feature_slice).to(device)
test_labels = torch.FloatTensor(test_label_slice).to(device)

# 调整标签维度以匹配输出 (N, 1)
if train_labels.dim() == 1:
    train_labels = train_labels.unsqueeze(1)
if test_labels.dim() == 1:
    test_labels = test_labels.unsqueeze(1)

# 创建 DataLoader
train_dataset = TensorDataset(train_features, train_labels)
train_loader = DataLoader(train_dataset, batch_size=config.batch_size, shuffle=True)

test_dataset = TensorDataset(test_features, test_labels)
test_loader = DataLoader(test_dataset, batch_size=config.batch_size, shuffle=False)


# =============================================================================
# LSTM 模型定义
# =============================================================================

class RULPredictor(nn.Module):
    """
    基于 LSTM 的 RUL 预测模型
    结构：3层 LSTM + Dropout + Dense
    """

    def __init__(self, input_dim, hidden_units, num_layers=3, dropout=0.2):
        super(RULPredictor, self).__init__()

        self.hidden_units = hidden_units
        self.num_layers = num_layers

        # LSTM 层
        # 第一层
        self.lstm_0 = nn.LSTM(
            input_size=input_dim,
            hidden_size=hidden_units[0],
            num_layers=1,
            batch_first=True
        )
        self.dropout_0 = nn.Dropout(dropout)

        # 第二层
        self.lstm_1 = nn.LSTM(
            input_size=hidden_units[0],
            hidden_size=hidden_units[1],
            num_layers=1,
            batch_first=True
        )
        self.dropout_1 = nn.Dropout(dropout)

        # 第三层
        self.lstm_2 = nn.LSTM(
            input_size=hidden_units[1],
            hidden_size=hidden_units[2],
            num_layers=1,
            batch_first=True
        )
        self.dropout_2 = nn.Dropout(dropout)

        # 全连接输出层
        self.fc = nn.Linear(hidden_units[2], 1)

    def forward(self, x):
        # 第一层 LSTM
        out, _ = self.lstm_0(x)
        out = self.dropout_0(out)

        # 第二层 LSTM
        out, _ = self.lstm_1(out)
        out = self.dropout_1(out)

        # 第三层 LSTM (只取最后一个时间步)
        out, _ = self.lstm_2(out)
        out = self.dropout_2(out)

        # 取序列最后一个时间步的输出
        out = out[:, -1, :]

        # 全连接层输出 RUL
        out = self.fc(out)

        return out


# 初始化模型
hidden_units = [100, 50, 25]  # 对应原模型的三层 LSTM 单元数
model = RULPredictor(
    input_dim=input_dim,
    hidden_units=hidden_units,
    dropout=0.2
).to(device)

# 打印模型结构
print(model)
logging.info(f"Model structure:\n{model}")

# 计算模型参数总数
total_params = sum(p.numel() for p in model.parameters())
trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
print(f"Total parameters: {total_params:,}")
print(f"Trainable parameters: {trainable_params:,}")

# =============================================================================
# 损失函数和优化器
# =============================================================================
criterion = nn.MSELoss()  # 均方误差
optimizer = optim.RMSprop(model.parameters(), lr=config.learning_rate)  # RMSprop 优化器

# 学习率调度器（可选）
scheduler = optim.lr_scheduler.ReduceLROnPlateau(
    optimizer,
    mode='min',
    factor=0.5,
    patience=5
)


# =============================================================================
# 训练函数
# =============================================================================

def train_epoch(model, train_loader, criterion, optimizer):
    """训练一个 epoch"""
    model.train()
    running_loss = 0.0
    running_mae = 0.0

    for batch_idx, (data, target) in enumerate(train_loader):
        # 前向传播
        optimizer.zero_grad()
        output = model(data)
        loss = criterion(output, target)

        # 反向传播
        loss.backward()
        optimizer.step()

        # 统计
        running_loss += loss.item()
        mae = torch.abs(output - target).mean()
        running_mae += mae.item()

        if batch_idx % 50 == 0:
            logging.info(f'Batch {batch_idx}/{len(train_loader)}, '
                         f'Loss: {loss.item():.6f}, MAE: {mae.item():.6f}')

    avg_loss = running_loss / len(train_loader)
    avg_mae = running_mae / len(train_loader)

    return avg_loss, avg_mae


def validate(model, test_loader, criterion):
    """验证模型"""
    model.eval()
    val_loss = 0.0
    val_mae = 0.0

    with torch.no_grad():
        for data, target in test_loader:
            output = model(data)
            loss = criterion(output, target)
            val_loss += loss.item()
            val_mae += torch.abs(output - target).mean().item()

    avg_loss = val_loss / len(test_loader)
    avg_mae = val_mae / len(test_loader)

    return avg_loss, avg_mae


# =============================================================================
# 可视化函数
# =============================================================================

def plot_results(y_pred, y_true):
    """
    绘制预测结果与真实值的对比图
    """
    num = len(y_pred)
    fig_verify = plt.figure(figsize=(60, 30))

    X = np.arange(1, num + 1)
    width = 0.35

    plt.bar(X, np.array(y_pred).reshape(num, ), width, color='r')
    plt.bar(X + width, np.array(y_true).reshape(num, ), width, color='b')

    plt.xticks(X)
    plt.title('Remaining Useful Life for each turbine')
    plt.ylabel('RUL')
    plt.xlabel('Turbine')
    plt.legend(['predicted', 'actual data'], loc='upper left')

    plt.show()
    fig_verify.savefig("lstm-pytorch-cmapss-model.png")
    logging.info("Plot saved to lstm-pytorch-cmapss-model.png")


# =============================================================================
# TensorBoard 支持 (可选)
# =============================================================================
try:
    from torch.utils.tensorboard import SummaryWriter

    use_tensorboard = True
    writer = SummaryWriter(log_dir="tensorboard-logs-pytorch")
    logging.info("TensorBoard enabled")
except ImportError:
    use_tensorboard = False
    logging.warning("TensorBoard not available, install with: pip install tensorboard")


# =============================================================================
# 早停类
# =============================================================================

class EarlyStopping:
    """早停机制"""

    def __init__(self, patience=10, min_delta=0.01):
        self.patience = patience
        self.min_delta = min_delta
        self.counter = 0
        self.best_loss = None
        self.early_stop = False

    def __call__(self, val_loss):
        if self.best_loss is None:
            self.best_loss = val_loss
        elif val_loss > self.best_loss - self.min_delta:
            self.counter += 1
            if self.counter >= self.patience:
                self.early_stop = True
        else:
            self.best_loss = val_loss
            self.counter = 0


# =============================================================================
# 主程序入口
# =============================================================================

if __name__ == '__main__':

    # 检查是否加载预训练权重
    if config.weights:
        if os.path.isfile(config.weights):
            model.load_state_dict(torch.load(config.weights))
            logging.info(f"Loaded weights from {config.weights}")
        else:
            raise ValueError("config.weights is not a valid filepath")
    else:
        # 训练新模式
        early_stopping = EarlyStopping(patience=10, min_delta=0.01)
        best_val_loss = float('inf')

        logging.info("Starting training...")

        for epoch in range(config.epochs):
            # 训练
            train_loss, train_mae = train_epoch(model, train_loader, criterion, optimizer)

            # 验证
            val_loss, val_mae = validate(model, test_loader, criterion)

            # 学习率调度
            scheduler.step(val_loss)

            # 记录日志
            logging.info(f'Epoch {epoch + 1}/{config.epochs}: '
                         f'Train Loss: {train_loss:.6f}, Train MAE: {train_mae:.6f}, '
                         f'Val Loss: {val_loss:.6f}, Val MAE: {val_mae:.6f}')

            # TensorBoard 记录
            if use_tensorboard:
                writer.add_scalar('Loss/train', train_loss, epoch)
                writer.add_scalar('Loss/val', val_loss, epoch)
                writer.add_scalar('MAE/train', train_mae, epoch)
                writer.add_scalar('MAE/val', val_mae, epoch)

            # 保存最佳模型
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                torch.save(model.state_dict(), 'vanilla-lstm-cmapss-weights_v0_best.pth')
                logging.info(f"Best model saved with val_loss: {val_loss:.6f}")

            # 早停检查
            early_stopping(val_loss)
            if early_stopping.early_stop:
                logging.info(f"Early stopping triggered at epoch {epoch + 1}")
                break

        # 保存最终模型
        weights_save_path = 'vanilla-lstm-cmapss-weights_v0.pth'
        torch.save(model.state_dict(), weights_save_path)
        logging.info(f"Final model saved as {weights_save_path}")

        if use_tensorboard:
            writer.close()

    # =============================================================================
    # 模型评估
    # =============================================================================
    model.eval()
    all_preds = []
    all_targets = []

    with torch.no_grad():
        for data, target in test_loader:
            output = model(data)
            all_preds.append(output.cpu().numpy())
            all_targets.append(target.cpu().numpy())

    y_pred = np.concatenate(all_preds, axis=0)
    y_true = np.concatenate(all_targets, axis=0)

    # 计算评估指标
    test_mse = np.mean((y_pred - y_true) ** 2)
    test_mae = np.mean(np.abs(y_pred - y_true))

    logging.info(f"Test MSE: {test_mse:.6f}, Test MAE: {test_mae:.6f}")

    # 计算 R² 决定系数
    ss_res = ((y_pred - y_true) ** 2).sum()
    y_mean = y_pred.mean()
    ss_tot = ((y_true - y_true.mean()) ** 2).sum()  # 修正：使用真实值的均值
    r2_score = 1 - ss_res / ss_tot

    logging.info(f'R² Score: {r2_score:.6f}')
    logging.info(f'Efficiency: {r2_score * 100:.2f}%')

    # =============================================================================
    # 可视化结果
    # =============================================================================
    plot_results(y_pred, y_true)
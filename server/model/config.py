import yaml
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Config:
    """模型配置类"""

    # 模型权重
    weights: Optional[str] = None

    # 训练参数
    epochs: int = 100
    batch_size: int = 32
    sequence_length: int = 32

    # 数据集
    fd_number: str = "1"
    data_dir: str = "C-MAPSS-Data"

    # 调试
    debug: bool = False

    # 模型结构
    learning_rate: float = 0.001
    hidden_units: int = 64
    dropout_rate: float = 0.2

    # 日志和保存
    log_dir: str = "logs"
    checkpoint_dir: str = "checkpoints"
    save_best_only: bool = True

    # 早停
    early_stopping_patience: int = 10

    @classmethod
    def from_yaml(cls, config_path: str) -> 'Config':
        """从 YAML 文件加载配置"""
        config_file = Path(config_path)

        if not config_file.exists():
            raise FileNotFoundError(f"配置文件不存在: {config_file}")

        with open(config_file, 'r', encoding='utf-8') as f:
            config_dict = yaml.safe_load(f)

        return cls(**config_dict)

    def to_yaml(self, config_path: str) -> None:
        """保存配置到 YAML 文件"""
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(self.__dict__, f, default_flow_style=False, allow_unicode=True)

    def __post_init__(self):
        """初始化后验证"""
        # 验证 fd_number
        if self.fd_number not in ['1', '2', '3', '4']:
            raise ValueError(f"fd_number 必须是 1-4，当前: {self.fd_number}")

        # 验证数据目录
        if not Path(self.data_dir).exists():
            print(f"⚠️  警告: 数据目录不存在: {self.data_dir}")
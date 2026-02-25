import numpy
import torch
from torch.utils.data import Dataset, DataLoader
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

# CMAPSS数据集列名
columns = ['id', 'cycle', 'setting1', 'setting2', 'setting3', 's1', 's2', 's3', 's4', 's5', 's6', 's7', 's8',
           's9', 's10', 's11', 's12', 's13', 's14', 's15', 's16', 's17', 's18', 's19', 's20', 's21']

feature_columns = ['setting1', 'setting2', 'setting3', 's1', 's2', 's3', 's4', 's5', 's6', 's7', 's8',
                   's9', 's10', 's11', 's12', 's13', 's14', 's15', 's16', 's17', 's18', 's19', 's20', 's21',
                   'cycle_norm']


class CMAPSSDataset():
    def __init__(self, fd_number, batch_size, sequence_length):
        """
        CMAPSS数据集加载器
        Args:
            fd_number: 数据集编号 (1-4)
            batch_size: 批次大小
            sequence_length: 序列长度（滑动窗口大小）
        """
        self.batch_size = batch_size
        self.sequence_length = sequence_length
        self.train_data = None
        self.test_data = None
        self.train_data_encoding = None
        self.test_data_encoding = None

        # \s+ 匹配一个或多个空格
        data = pd.read_csv("CMAPSSData/train_FD00" + fd_number + ".txt", delimiter=r"\s+", header=None)
        data.columns = columns

        # 计算该数据集包含的engine数目
        self.engine_size = data['id'].unique().max()

        # 计算每一行的剩余cycle
        rul = pd.DataFrame(data.groupby('id')['cycle'].max()).reset_index()
        rul.columns = ['id', 'max']
        data = data.merge(rul, on=['id'], how='left')
        data['RUL'] = data['max'] - data['cycle']
        data.drop(['max'], axis=1, inplace=True)

        # 将id之外的列正规化
        self.std = StandardScaler()
        data['cycle_norm'] = data['cycle']
        cols_normalize = data.columns.difference(['id', 'cycle', 'RUL'])
        norm_data = pd.DataFrame(self.std.fit_transform(data[cols_normalize]),
                                 columns=cols_normalize, index=data.index)
        join_data = data[data.columns.difference(cols_normalize)].join(norm_data)
        self.train_data = join_data.reindex(columns=data.columns)

        # 读取测试数据集并执行相同操作
        test_data = pd.read_csv("CMAPSSData/test_FD00" + fd_number + ".txt", delimiter=r"\s+", header=None)
        test_data.columns = columns
        truth_data = pd.read_csv("CMAPSSData/RUL_FD00" + fd_number + ".txt", delimiter=r"\s+", header=None)
        truth_data.columns = ['truth']
        truth_data['id'] = truth_data.index + 1

        test_rul = pd.DataFrame(test_data.groupby('id')['cycle'].max()).reset_index()
        test_rul.columns = ['id', 'elapsed']
        test_rul = test_rul.merge(truth_data, on=['id'], how='left')
        test_rul['max'] = test_rul['elapsed'] + test_rul['truth']

        test_data = test_data.merge(test_rul, on=['id'], how='left')
        test_data['RUL'] = test_data['max'] - test_data['cycle']
        test_data.drop(['max'], axis=1, inplace=True)

        test_data['cycle_norm'] = test_data['cycle']
        norm_test_data = pd.DataFrame(self.std.fit_transform(test_data[cols_normalize]),
                                      columns=cols_normalize, index=test_data.index)
        join_test_data = test_data[test_data.columns.difference(cols_normalize)].join(norm_test_data)
        self.test_data = join_test_data.reindex(columns=test_data.columns)

    def get_train_data(self):
        """获取训练数据 DataFrame"""
        return self.train_data

    def get_test_data(self):
        """获取测试数据 DataFrame"""
        return self.test_data

    def get_feature_slice(self, input_data) -> numpy.ndarray:
        """
        将输入数据转换为特征切片 (samples, time steps, features)
        Returns:
            numpy.ndarray: 形状为 (num_samples, sequence_length, num_features)
        """

        def reshapeFeatures(input, columns, sequence_length):
            data = input[columns].values
            num_elements = data.shape[0]
            for start, stop in zip(range(0, num_elements - sequence_length), range(sequence_length, num_elements)):
                yield (data[start:stop, :])

        feature_list = [list(reshapeFeatures(input_data[input_data['id'] == i], feature_columns, self.sequence_length))
                        for i in range(1, self.engine_size + 1) if
                        len(input_data[input_data['id'] == i]) > self.sequence_length]

        feature_array = np.concatenate(list(feature_list), axis=0).astype(np.float32)

        length = len(feature_array) // self.batch_size
        return feature_array[:length * self.batch_size]

    def get_engine_id(self, input_data):
        """
        获取发动机ID序列
        用于VAE中需要对每个engine单独进行滑动窗口编码的场景
        Returns:
            numpy.ndarray: 发动机ID数组
        """

        def reshapeLabels(input, sequence_length, columns=['id']):
            data = input[columns].values
            num_elements = data.shape[0]
            return (data[sequence_length:num_elements, :])

        label_list = [reshapeLabels(input_data[input_data['id'] == i], self.sequence_length)
                      for i in range(1, self.engine_size + 1)]
        label_array = np.concatenate(label_list).astype(np.int8)
        length = len(label_array) // self.batch_size
        return label_array[:length * self.batch_size]

    def get_label_slice(self, input_data):
        """
        获取RUL标签切片
        Returns:
            numpy.ndarray: 形状为 (num_samples, 1)
        """

        def reshapeLabels(input, sequence_length, columns=['RUL']):
            data = input[columns].values
            num_elements = data.shape[0]
            return (data[sequence_length:num_elements, :])

        label_list = [reshapeLabels(input_data[input_data['id'] == i], self.sequence_length)
                      for i in range(1, self.engine_size + 1)]
        label_array = np.concatenate(label_list).astype(np.float32)
        length = len(label_array) // self.batch_size
        return label_array[:length * self.batch_size]

    def get_last_data_slice(self, input_data):
        """
        每个engine只取最后sequence_length个时间步（用于最终评估）

        Returns:
            tuple: (features, labels) 都是numpy数组
        """
        num_engine = input_data['id'].unique().max()
        test_feature_list = [input_data[input_data['id'] == i][feature_columns].values[-self.sequence_length:]
                             for i in range(1, num_engine + 1) if
                             len(input_data[input_data['id'] == i]) >= self.sequence_length]
        test_feature_array = np.asarray(test_feature_list).astype(np.float32)
        length_test = len(test_feature_array) // self.batch_size

        test_label_list = [input_data[input_data['id'] == i]['RUL'].values[-1:]
                           for i in range(1, num_engine + 1) if
                           len(input_data[input_data['id'] == i]) >= self.sequence_length]
        test_label_array = np.asarray(test_label_list).astype(np.float32)
        length_label = len(test_label_array) // self.batch_size

        return test_feature_array[:length_test * self.batch_size], test_label_array[:length_label * self.batch_size]

    def set_test_data_encoding(self, test_data_encoding):
        self.test_data_encoding = test_data_encoding

    def set_train_data_encoding(self, train_data_encoding):
        self.train_data_encoding = train_data_encoding

    # =============================================================================
    # PyTorch 新增方法
    # =============================================================================

    def get_train_tensors(self, device='cpu'):
        """
        获取训练数据的PyTorch张量
        Args:
            device: 设备 ('cpu' 或 'cuda')

        Returns:
            tuple: (features, labels) 都是torch.Tensor
        """
        features = self.get_feature_slice(self.train_data)
        labels = self.get_label_slice(self.train_data)

        # 转换为PyTorch张量
        features_tensor = torch.from_numpy(features).to(device)
        labels_tensor = torch.from_numpy(labels).to(device)

        return features_tensor, labels_tensor

    def get_test_tensors(self, device='cpu'):
        """
        获取测试数据的PyTorch张量（完整序列）

        Args:
            device: 设备 ('cpu' 或 'cuda')

        Returns:
            tuple: (features, labels) 都是torch.Tensor
        """
        features = self.get_feature_slice(self.test_data)
        labels = self.get_label_slice(self.test_data)

        features_tensor = torch.from_numpy(features).to(device)
        labels_tensor = torch.from_numpy(labels).to(device)

        return features_tensor, labels_tensor

    def get_last_test_tensors(self, device='cpu'):
        """
        获取测试数据的PyTorch张量（仅最后一个序列，用于评估）

        Args:
            device: 设备 ('cpu' 或 'cuda')

        Returns:
            tuple: (features, labels) 都是torch.Tensor
        """
        features, labels = self.get_last_data_slice(self.test_data)

        features_tensor = torch.from_numpy(features).to(device)
        labels_tensor = torch.from_numpy(labels).to(device)

        return features_tensor, labels_tensor

    def get_train_dataloader(self, device='cpu', shuffle=True):
        """
        创建训练数据的PyTorch DataLoader

        Args:
            device: 设备 ('cpu' 或 'cuda')
            shuffle: 是否打乱数据

        Returns:
            DataLoader: PyTorch数据加载器
        """
        features, labels = self.get_train_tensors(device)

        # 创建TensorDataset
        dataset = torch.utils.data.TensorDataset(features, labels)

        # 创建DataLoader
        dataloader = DataLoader(
            dataset,
            batch_size=self.batch_size,
            shuffle=shuffle,
            drop_last=False
        )

        return dataloader

    def get_test_dataloader(self, device='cpu', shuffle=False):
        """
        创建测试数据的PyTorch DataLoader（完整序列）

        Args:
            device: 设备 ('cpu' 或 'cuda')
            shuffle: 是否打乱数据

        Returns:
            DataLoader: PyTorch数据加载器
        """
        features, labels = self.get_test_tensors(device)

        dataset = torch.utils.data.TensorDataset(features, labels)
        dataloader = DataLoader(
            dataset,
            batch_size=self.batch_size,
            shuffle=shuffle,
            drop_last=False
        )

        return dataloader

    def get_last_test_dataloader(self, device='cpu', shuffle=False):
        """
        创建测试数据的PyTorch DataLoader（仅最后一个序列）
        Args:
            device: 设备 ('cpu' 或 'cuda')
            shuffle: 是否打乱数据

        Returns:
            DataLoader: PyTorch数据加载器
        """
        features, labels = self.get_last_test_tensors(device)

        dataset = torch.utils.data.TensorDataset(features, labels)
        dataloader = DataLoader(
            dataset,
            batch_size=self.batch_size,
            shuffle=shuffle,
            drop_last=False
        )

        return dataloader


# =============================================================================
# PyTorch Dataset 类（替代方案，更符合PyTorch风格）
# =============================================================================

class CMAPSSPyTorchDataset(Dataset):
    """
    纯PyTorch风格的CMAPSS数据集类
    支持动态加载和transforms
    """

    def __init__(self, fd_number, sequence_length, mode='train', transform=None):
        """
        Args:
            fd_number: 数据集编号 (1-4)
            sequence_length: 序列长度
            mode: 'train' 或 'test'
            transform: 可选的数据变换
        """
        self.sequence_length = sequence_length
        self.mode = mode
        self.transform = transform

        # 加载原始数据
        data = pd.read_csv(f"CMAPSSData/{mode}_FD00{fd_number}.txt", delimiter=r"\s+", header=None)
        data.columns = columns

        self.engine_size = data['id'].unique().max()

        # 计算RUL
        rul = pd.DataFrame(data.groupby('id')['cycle'].max()).reset_index()
        rul.columns = ['id', 'max']
        data = data.merge(rul, on=['id'], how='left')
        data['RUL'] = data['max'] - data['cycle']
        data.drop(['max'], axis=1, inplace=True)

        # 标准化
        self.std = StandardScaler()
        data['cycle_norm'] = data['cycle']
        cols_normalize = data.columns.difference(['id', 'cycle', 'RUL'])
        norm_data = pd.DataFrame(self.std.fit_transform(data[cols_normalize]),
                                 columns=cols_normalize, index=data.index)
        join_data = data[data.columns.difference(cols_normalize)].join(norm_data)
        self.data = join_data.reindex(columns=data.columns)

        # 如果是测试集，加载真实RUL
        if mode == 'test':
            truth_data = pd.read_csv(f"CMAPSSData/RUL_FD00{fd_number}.txt", delimiter=r"\s+", header=None)
            truth_data.columns = ['truth']
            truth_data['id'] = truth_data.index + 1

            test_rul = pd.DataFrame(self.data.groupby('id')['cycle'].max()).reset_index()
            test_rul.columns = ['id', 'elapsed']
            test_rul = test_rul.merge(truth_data, on=['id'], how='left')
            test_rul['max'] = test_rul['elapsed'] + test_rul['truth']

            self.data = self.data.merge(test_rul[['id', 'max']], on=['id'], how='left')
            self.data['RUL'] = self.data['max'] - self.data['cycle']
            self.data.drop(['max'], axis=1, inplace=True)

        # 预生成所有序列
        self.sequences = []
        self.labels = []
        self.engine_ids = []

        for engine_id in range(1, self.engine_size + 1):
            engine_data = self.data[self.data['id'] == engine_id]
            if len(engine_data) <= sequence_length:
                continue

            values = engine_data[feature_columns].values
            rul_values = engine_data['RUL'].values

            for start in range(len(values) - sequence_length):
                self.sequences.append(values[start:start + sequence_length])
                self.labels.append(rul_values[start + sequence_length])
                self.engine_ids.append(engine_id)

        self.sequences = np.array(self.sequences, dtype=np.float32)
        self.labels = np.array(self.labels, dtype=np.float32)

    def __len__(self):
        return len(self.sequences)

    def __getitem__(self, idx):
        sequence = self.sequences[idx]
        label = self.labels[idx]

        if self.transform:
            sequence = self.transform(sequence)

        return torch.from_numpy(sequence), torch.tensor(label, dtype=torch.float32)


if __name__ == "__main__":
    print("=" * 60)
    print("CMAPSS Dataset PyTorch 版本测试")
    print("=" * 60)

    # 测试原始类
    datasets = CMAPSSDataset(fd_number='1', batch_size=10, sequence_length=50)

    train_data = datasets.get_train_data()
    train_feature_slice = datasets.get_feature_slice(train_data)
    train_label_slice = datasets.get_label_slice(train_data)
    train_engine_id = datasets.get_engine_id(train_data)

    print("\n--- 原始NumPy数组 ---")
    print("train_data.shape: {}".format(train_data.shape))
    print("train_feature_slice.shape: {}".format(train_feature_slice.shape))
    print("train_label_slice.shape: {}".format(train_label_slice.shape))
    print("train_engine_id.shape: {}".format(train_engine_id.shape))

    test_data = datasets.get_test_data()
    print("test_data.shape: {}".format(test_data.shape))
    test_feature_slice = datasets.get_feature_slice(test_data)
    test_label_slice = datasets.get_label_slice(test_data)
    test_engine_id = datasets.get_engine_id(test_data)
    print("test_feature_slice.shape: {}".format(test_feature_slice.shape))
    print("test_label_slice.shape: {}".format(test_label_slice.shape))
    print("test_engine_id.shape: {}".format(test_engine_id.shape))

    # 测试PyTorch张量
    print("\n--- PyTorch张量 ---")
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"Using device: {device}")

    train_features_tensor, train_labels_tensor = datasets.get_train_tensors(device)
    print(f"train_features_tensor shape: {train_features_tensor.shape}, dtype: {train_features_tensor.dtype}")
    print(f"train_labels_tensor shape: {train_labels_tensor.shape}, dtype: {train_labels_tensor.dtype}")
    print(f"train_features_tensor device: {train_features_tensor.device}")

    # 测试DataLoader
    print("\n--- PyTorch DataLoader ---")
    train_loader = datasets.get_train_dataloader(device, shuffle=True)
    print(f"Number of batches: {len(train_loader)}")

    for batch_idx, (batch_features, batch_labels) in enumerate(train_loader):
        print(f"Batch {batch_idx}: features {batch_features.shape}, labels {batch_labels.shape}")
        if batch_idx >= 2:  # 只打印前3个batch
            break

    # 测试纯PyTorch Dataset
    print("\n--- 纯PyTorch Dataset类 ---")
    pytorch_dataset = CMAPSSPyTorchDataset(fd_number='1', sequence_length=50, mode='train')
    print(f"Dataset size: {len(pytorch_dataset)}")

    sample_seq, sample_label = pytorch_dataset[0]
    print(f"Sample sequence shape: {sample_seq.shape}")
    print(f"Sample label: {sample_label}")

    pytorch_loader = DataLoader(pytorch_dataset, batch_size=10, shuffle=True)
    for batch_idx, (batch_features, batch_labels) in enumerate(pytorch_loader):
        print(f"PyTorch Batch {batch_idx}: features {batch_features.shape}, labels {batch_labels.shape}")
        if batch_idx >= 2:
            break

    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)
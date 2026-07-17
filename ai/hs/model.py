"""
ResNet9 (fast.ai 스타일, from scratch, 1채널 64x64 대응)
"""
import torch.nn as nn


def conv_block(in_ch, out_ch, pool=False, dropout_p=0.0):
    layers = [
        nn.Conv2d(in_ch, out_ch, kernel_size=3, padding=1, bias=False),
        nn.BatchNorm2d(out_ch),
        nn.ReLU(inplace=True)
    ]
    if pool:
        layers.append(nn.MaxPool2d(2))
    if dropout_p > 0:
        layers.append(nn.Dropout2d(dropout_p))
    return nn.Sequential(*layers)


class ResidualBlock(nn.Module):
    def __init__(self, channels):
        super().__init__()
        self.conv1 = conv_block(channels, channels)
        self.conv2 = conv_block(channels, channels)

    def forward(self, x):
        out = self.conv1(x)
        out = self.conv2(out)
        return out + x


class ResNet9(nn.Module):
    def __init__(self, num_classes):
        super().__init__()
        self.stem = conv_block(1, 64)
        self.layer1 = conv_block(64, 128, pool=True)
        self.res1 = ResidualBlock(128)

        self.layer2 = conv_block(128, 256, pool=True, dropout_p=0.2)
        self.layer3 = conv_block(256, 512, pool=True, dropout_p=0.2)
        self.res2 = ResidualBlock(512)

        self.pool = nn.AdaptiveAvgPool2d(1)
        self.dropout = nn.Dropout(0.4)
        self.fc = nn.Linear(512, num_classes)

    def forward(self, x):
        x = self.stem(x)
        x = self.layer1(x)
        x = self.res1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.res2(x)
        x = self.pool(x)
        x = x.flatten(1)
        x = self.dropout(x)
        return self.fc(x)
'''
    code by Tae Hwan Jung @graykode
    code reference : https://github.com/kuangliu/pytorch-cifar/blob/master/models/densenet.py
'''
import math
import torch
import torch.nn as nn
from modelsummary import summary

class Bottleneck(nn.Module):
    def __init__(self, in_channel, growth_rate):
        super(Bottleneck, self).__init__()
        self.composite1 = nn.Sequential(
            nn.BatchNorm2d(in_channel),
            nn.ReLU(),
            nn.Conv2d(in_channel, 4 * growth_rate, kernel_size=1, bias=False)
        )
        self.composite2 = nn.Sequential(
            nn.BatchNorm2d(4 * growth_rate),
            nn.ReLU(),
            nn.Conv2d(4 * growth_rate, growth_rate, kernel_size=3, padding=1, bias=False)
        )
    def forward(self, x): # in_channel > growth_rate
        out = self.composite1(x) # in_channel > 4*growth_rate
        out = self.composite2(out) # 4*growth_rate > growth_rate
        out = torch.cat([out, x], 1) # 1 dim is channel
        return out

class Transition(nn.Module):
    def __init__(self, in_channel, out_channel):
        super(Transition, self).__init__()
        self.composite = nn.Sequential(
            nn.BatchNorm2d(in_channel),
            nn.ReLU(),
            nn.Conv2d(in_channel, out_channel, kernel_size=1, bias=False),
            nn.AvgPool2d(kernel_size=2)
        )
    def forward(self, x):
        return self.composite(x)

class DenseNet(nn.Module):
    def __init__(self, type_block, num_blocks, growth_rate=12, reduction=0.5, num_classes=2):
        super(DenseNet, self).__init__()
        self.growth_rate = growth_rate

        in_channel = 2 * growth_rate # The initial convolution layer comprises 2k convolutions of size 7×7 with stride 2
        self.conv1 =  nn.Conv2d(3, in_channel, kernel_size=7, stride=2, padding=1, bias=False) # 112 = (227-7+2*1)/2+1
        self.max_pooling = nn.MaxPool2d(kernel_size=3, stride=2)

        self.dense1 = self.make_dense_layers(type_block, in_channel, num_blocks[0])
        in_channel += num_blocks[0]*growth_rate
        out_channel = int(math.floor(in_channel * reduction))
        self.trans1 = Transition(in_channel, out_channel) # Transite channel in_channel > out_channel
        in_channel = out_channel

        self.dense2 = self.make_dense_layers(type_block, in_channel, num_blocks[1])
        in_channel += num_blocks[1] * growth_rate
        out_channel = int(math.floor(in_channel * reduction))
        self.trans2 = Transition(in_channel, out_channel)
        in_channel = out_channel

        self.dense3 = self.make_dense_layers(type_block, in_channel, num_blocks[2])
        in_channel += num_blocks[2] * growth_rate
        out_planes = int(math.floor(in_channel * reduction))
        self.trans3 = Transition(in_channel, out_planes)
        in_channel = out_planes

        self.dense4 = self.make_dense_layers(type_block, in_channel, num_blocks[3])
        in_channel += num_blocks[3] * growth_rate

        self.classifier = nn.Sequential(
            nn.BatchNorm2d(in_channel),
            nn.ReLU(),
            nn.AvgPool2d(kernel_size=7)
        )
        self.linear = nn.Linear(in_channel, num_classes)

    def make_dense_layers(self, type_block, in_channel, num_block):
        layers = []
        for i in range(num_block):
            layers.append(type_block(in_channel, self.growth_rate))
            in_channel += self.growth_rate
        return nn.Sequential(*layers)

    def forward(self, x):
        out = self.max_pooling(self.conv1(x))
        out = self.trans1(self.dense1(out))
        out = self.trans2(self.dense2(out))
        out = self.trans3(self.dense3(out))
        out = self.dense4(out)
        out = self.classifier(out)
        out = out.view(out.size(0), -1)
        out = self.linear(out)
        return out

def DenseNet121():
    return DenseNet(Bottleneck, [6,12,24,16], growth_rate=32)

def DenseNet169():
    return DenseNet(Bottleneck, [6,12,32,32], growth_rate=32)

def DenseNet201():
    return DenseNet(Bottleneck, [6,12,48,32], growth_rate=32)

def DenseNet161():
    return DenseNet(Bottleneck, [6,12,36,24], growth_rate=48)

# Please Select model by index
model = [DenseNet121(), DenseNet161(), DenseNet169(), DenseNet201()][3]
print(model)
summary(model, torch.zeros((1, 3, 227, 227)))
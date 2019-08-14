'''
    code by Tae Hwan Jung @graykode
    reference : https://github.com/kuangliu/pytorch-cifar/blob/master/models/resnet.py
'''
import torch
import torch.nn as nn
from modelsummary import summary

class BasicBlock(nn.Module):
    expansion = 1
    def __init__(self, in_channel, out_channel, stride=1):
        super(BasicBlock, self).__init__()
        self.features = nn.Sequential(
            nn.Conv2d(in_channel, out_channel, kernel_size=3, stride=stride, padding=1, bias=False),
            nn.BatchNorm2d(out_channel),
            nn.ReLU(),
            nn.Conv2d(out_channel, out_channel, kernel_size=3, stride=1, padding=1, bias=False),
            nn.BatchNorm2d(out_channel)
        )
        # make shortcut
        self.residual = nn.Sequential(nn.ReLU())
        if stride != 1 or in_channel != self.expansion * out_channel:
            # ResNet34 fig3 in paper, case of dot-line
            self.residual = nn.Sequential(
                # output channel is expansion * current channel
                nn.Conv2d(in_channel, self.expansion * out_channel, kernel_size=1, stride=stride, bias=False),
                nn.BatchNorm2d(self.expansion * out_channel),
                nn.ReLU()
            )

    def forward(self, x):
        out = self.features(x)
        out += self.residual(x) # intput is not out!
        return out

class Bottleneck(nn.Module):
    expansion = 4
    def __init__(self, in_channel, out_channel, stride=1):
        super(Bottleneck, self).__init__()
        self.features = nn.Sequential(
            nn.Conv2d(in_channel, out_channel, kernel_size=3, stride=stride, padding=1, bias=False),
            nn.BatchNorm2d(out_channel),
            nn.ReLU(),
            nn.Conv2d(out_channel, out_channel, kernel_size=3, stride=1, padding=1, bias=False),
            nn.BatchNorm2d(out_channel),
            nn.ReLU(),
            nn.Conv2d(out_channel, self.expansion * out_channel, kernel_size=1, bias=False),
            nn.BatchNorm2d(self.expansion * out_channel)
        )
        self.residual = nn.Sequential(nn.ReLU())
        if stride != 1 or in_channel != self.expansion * out_channel:
            # ResNet34 fig3 in paper, case of dot-line
            self.residual = nn.Sequential(
                # output channel is expansion * current channel
                nn.Conv2d(in_channel, self.expansion * out_channel, kernel_size=1, stride=stride, bias=False),
                nn.BatchNorm2d(self.expansion * out_channel),
                nn.ReLU()
            )

    def forward(self, x):
        out = self.features(x)
        out += self.residual(x)  # intput is not out!
        return out

# out_channel : (width(=height) - filter_size + 2*padding)/stride + 1
class ResNet(nn.Module):
    def __init__(self, type_block , num_blocks, num_classes=2):
        super(ResNet, self).__init__()
        self.in_channel = 64
        self.features = nn.Sequential(
            nn.Conv2d(3, 64, kernel_size=3, stride=2, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.AvgPool2d(kernel_size=3, stride=2),
            self.make_layer(type_block, 64,  num_blocks[0], stride=1),
            self.make_layer(type_block, 128, num_blocks[1], stride=2),
            self.make_layer(type_block, 256, num_blocks[2], stride=2),
            self.make_layer(type_block, 512, num_blocks[3], stride=2),
            nn.AvgPool2d(kernel_size=7)
        )
        self.linear = nn.Linear(512 * type_block.expansion, num_classes)

    def make_layer(self, type_block, in_channel, num_blocks, stride):
        strides = [stride] + [1] * (num_blocks - 1) # only stride of first layer is not one.
        layers = []
        for stride in strides:
            layers.append(type_block(self.in_channel, in_channel, stride))
            self.in_channel = in_channel * type_block.expansion
        return nn.Sequential(*layers)

    def forward(self, x): # x : [batch_size, 3, 227, 227]
        out = self.features(x)
        out = out.view(out.size(0), -1)
        out = self.linear(out)
        return out

def ResNet18():
    return ResNet(BasicBlock, [2,2,2,2])

def ResNet34():
    return ResNet(BasicBlock, [3,4,6,3])

def ResNet50():
    return ResNet(Bottleneck, [3,4,6,3])

def ResNet101():
    return ResNet(Bottleneck, [3,4,23,3])

def ResNet152():
    return ResNet(Bottleneck, [3,8,36,3])

# Please Select model by index
model = [ResNet18(), ResNet34(), ResNet50(), ResNet101(), ResNet152()][3]
print(model)
summary(model, torch.zeros((1, 3, 227, 227)))
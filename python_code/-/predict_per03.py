import os
import sys
import json
import cv2
import numpy as np
import nibabel as nib
import torch
import torchvision.transforms as transforms
from torch.utils.data import Dataset, DataLoader
from torchvision.models import resnet18
import matplotlib.pyplot as plt

#​normalize이며, 하나의 입력 인수를 받습니다. 이 인수는 'tensor'라는 이름의 변수로 전달됩니다.
def normalize(tensor):
    return (tensor - tensor.min()) / (tensor.max() - tensor.min())

#주어진 2D 이미지를 흑백(grayscale)으로 시각화하는 함수를 정의합니다. 함수의 이름은 visualize_slice이며, 두 개의 입력 인수를 받습니다: image와 title.
def visualize_slice(image, title):
    plt.imshow(image, cmap="gray")
    plt.title(title)
    plt.axis("off")
    plt.show()


# 기존에 정의한 함수들은 그대로 사용합니다.
def modify_resnet18_channels(model, in_channels=4):
    old_conv = model.conv1
    new_conv = torch.nn.Conv2d(in_channels, 64, kernel_size=7, stride=2, padding=3, bias=False)
    new_conv.weight.data[:, :3, :, :] = old_conv.weight.data
    new_conv.weight.data[:, 3:, :, :] = 0  # 초기 가중치를 0으로 설정
    model.conv1 = new_conv   


#뇌 종양 데이터셋을 나타내는 사용자 정의 파이토치(PyTorch) Dataset 클래스를 정의합니다. 클래스 이름은 BrainTumorDataset이며, torch.utils.data.Dataset을 상속받습니다.
class BrainTumorDataset(Dataset):
    def __init__(self, data, transform=None):
        self.data = data
        self.transform = transform

    def __getitem__(self, idx):
        image_path = self.data[idx]['image']
        image = nib.load(image_path).get_fdata()
        image = np.array(image, dtype=np.float32)

        ## 이미지를 2차원으로 변경
        #image = image.squeeze()
        
        # 이미지의 중앙 슬라이스만 사용하여 2D 이미지로 변환
        image = image[:, :, image.shape[2] // 2]

        label = self.data[idx]['label']
        
        if self.transform:
            image = self.transform(image)

        return image, label

    def __len__(self):
        return len(self.data)
    


def main():
    with open("D:\\python\\deep\\Task01_BrainTumour\\dataset.json", "r") as f:
        dataset = json.load(f)

    train_transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Lambda(normalize)
    ])

    train_data = BrainTumorDataset(dataset['training'], transform=train_transform)
    train_loader = DataLoader(train_data, batch_size=1, shuffle=True)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = resnet18(pretrained=True).to(device)
    modify_resnet18_channels(model)
    model.eval()

    # 모델 저장 코드를 메인 함수에서 삭제합니다.
    with torch.no_grad():
        for images, labels in train_loader:
            images = images.to(device)
            outputs = model(images)
            lesion_map = (outputs > 0.5).float()
            lesion_map = lesion_map.squeeze().cpu().numpy()
            resized_lesion_map = cv2.resize(lesion_map, (240, 240), interpolation=cv2.INTER_NEAREST)
            image_slice = images.squeeze().cpu().numpy()[0]
            visualize_slice(image_slice, "Original MRI Slice")
            visualize_slice(resized_lesion_map, "Lesion Map")

def predict(model, input_file, output_file):
    input_image = nib.load(input_file).get_fdata()
    input_image = np.array(input_image, dtype=np.float32)
    input_image = input_image[:, :, input_image.shape[2] // 2]

    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Lambda(normalize)
    ])
    input_image = transform(input_image)
    input_image = input_image.unsqueeze(0)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    input_image = input_image.to(device)

    with torch.no_grad():
        output = model(input_image)
        #score = output[0, 0].item()
        score = torch.max(output).item()
        #output 텐서에서 원하는 요소를 선택하는 방법을 정의할 수도 있습니다.
        #예를 들어, 최대 값을 가져오려면:  score = torch.max(output).item()

    with open(output_file, "w") as f:
        f.write(f"Prediction Score: {score}\n")

    print(f"Prediction Score: {score}")

if __name__ == "__main__":
    input_file = sys.argv[1]
    output_file = "output.txt"
    model_path = "D:\\python\\deep\\Task01_BrainTumour\\model.pth"

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = resnet18(pretrained=False).to(device)
    modify_resnet18_channels(model)
    model.load_state_dict(torch.load(model_path))
    model.eval()

    # 예측 수행
    predict(model, input_file, output_file)

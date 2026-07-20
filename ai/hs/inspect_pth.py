"""
resnet9_wafer.pth 안에 뭐가 들었는지 확인하는 스크립트.
가중치를 실제로 쓰려는 게 아니라, 구조/크기만 훑어볼 때 씀.

"""
import torch

state_dict = torch.load('resnet9_wafer.pth', map_location='cpu')

print(f"총 레이어(파라미터 텐서) 개수: {len(state_dict)}")
print(f"{'레이어 이름':<40}{'shape':<25}{'파라미터 수'}")
total = 0
for name, tensor in state_dict.items():
    n = tensor.numel()
    total += n
    print(f"{name:<40}{str(tuple(tensor.shape)):<25}{n:,}")
print(f"\n총 파라미터 수: {total:,}")
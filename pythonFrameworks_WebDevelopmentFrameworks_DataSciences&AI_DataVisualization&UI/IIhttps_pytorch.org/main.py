'''ModuleNotFoundError: No module named 'torch' '''
import torch
'''import pytorch'''

data = [[1, 2], [3, 4]]
x_data = torch.tensor(data)
print(f"Hello World Tensor:\n{x_data}")

print(f"CUDA available: {torch.cuda.is_available()}")
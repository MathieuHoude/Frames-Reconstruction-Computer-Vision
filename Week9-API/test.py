import torch
import numpy as np

model_file = './app/model.pt'
model = torch.jit.load(model_file)
# print(model.eval())
x = 0.7
tensor = torch.tensor([x], dtype=torch.float)
prediction = model(tensor)
print(prediction.item())

y = 15*x**2+5*x+8-3*np.exp(1+x)+5*np.log(x+0.5)

print(y)
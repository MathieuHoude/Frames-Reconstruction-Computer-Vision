from multiprocessing.sharedctypes import Value
import torch
import json
import numpy as np

import torch.nn as nn
import torch.nn.functional as F

model_file = '/opt/ml/model.pt'
model = torch.jit.load(model_file)

def lambda_handler(event, _):
    try:
        data = json.loads(event['body'])
        input = float(data['input'])
        if 0 <= input <= 1:
            tensor = torch.tensor([input], dtype=torch.float)
            prediction = model(tensor)

            return {
                'statusCode': 200,
                'body': json.dumps(
                    {
                        "predicted_value": prediction.item(),
                    }
                )
            }
        else:
            return {
                'statusCode': 400,
                'body': json.dumps(
                    {
                        "error": "Invalid input, please use a number between 0 and 1.",
                    }
                )
            }
    except ValueError:
        return {
                'statusCode': 400,
                'body': json.dumps(
                    {
                        "error": "Invalid input, must be numeric",
                    }
                )
            }

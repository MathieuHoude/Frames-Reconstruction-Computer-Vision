FROM public.ecr.aws/lambda/python:3.9

COPY app.py requirements.txt ./
COPY model.pt /opt/ml/model.pt

RUN /var/lang/bin/python3.9 -m pip install --upgrade pip
RUN python3.9 -m pip install -r requirements.txt -t .

CMD ["app.lambda_handler"]

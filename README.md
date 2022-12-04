Prerequirements:

- Node 18.x
- CDK

```
$ aws configure
```

Installation:

```
$ source .venv/bin/activate
$ pip install -r requirements.txt
```

Running:
```
$ cdk bootstrap  # Only if you never ran CDK on AWS account yet
$ cdk synth
$ cdk deploy
```
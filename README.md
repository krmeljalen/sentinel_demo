# Prerequirements:

- Python 3.8+
- Node 18.x
- CDK 2.x
- awscli 2.x

Configure your aws client, choose region and put in AWS key and secret
```
$ aws configure
```

Edit config.py.dist and copy it to config.py!

# Installation:

In cloned directory:

```
$ python3 -m venv .venv
$ source .venv/bin/activate
$ pip install -r requirements.txt
```

# Running:

It's as simple as:

```
$ cdk bootstrap  # Only if you never ran CDK on AWS account yet
$ cdk synth # Verify cf template gets generated and no errors
$ cdk deploy
```

# Deploy on repo change:

Code will hook up to main branch of github and listen to merges.
Once merge happens it will run pipeline in these stages:

 - Checkout source
 - Build docker image
 - Wait for approval (You need to click on console to approve deploy)
 - Deploy to ECS Fargate
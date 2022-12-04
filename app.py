#!/usr/bin/env python3
import aws_cdk as cdk

from sentinel_cdk.sentinel_cdk_stack import SentinelCdkStack

app = cdk.App()
base = SentinelCdkStack(app, "SentinelCdkStack",)

app.synth()

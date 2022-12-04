import aws_cdk as core
import aws_cdk.assertions as assertions

from sentinel_cdk.sentinel_cdk_stack import SentinelCdkStack

# example tests. To run these tests, uncomment this file along with the example
# resource in sentinel_cdk/sentinel_cdk_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = SentinelCdkStack(app, "sentinel-cdk")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })

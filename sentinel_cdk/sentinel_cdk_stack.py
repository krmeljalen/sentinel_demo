from aws_cdk import (
    aws_s3 as aws_s3,
    aws_ecr,
    aws_codebuild,
    aws_ec2,
    CfnOutput, Duration, RemovalPolicy, Stack
)
from constructs import Construct

class SentinelCdkStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # we will need ECS Cluster so lets create VPC for it
        vpc = aws_ec2.Vpc(self, "SentinelVPC",
            cidr="10.0.0.0/16"
        )

        # ecr repo to push sentinel docker
        ecr = aws_ecr.Repository(
            self, "ECR",
            repository_name=f"Sentinel",
            removal_policy=RemovalPolicy.DESTROY
        )

        # codebuild that builds docker image and pushes it to ECR
        docker_build = aws_codebuild.PipelineProject(
            self, "DockerBuild",
            project_name=f"Sentinel-Build",
            build_spec=aws_codebuild.BuildSpec.from_source_filename(
                filename='sentinel_app/buildspec.yml'),
            environment=aws_codebuild.BuildEnvironment(
                privileged=True,
            ),
            environment_variables={
                'ecr': aws_codebuild.BuildEnvironmentVariable(
                    value=ecr.repository_uri),
                'tag': aws_codebuild.BuildEnvironmentVariable(
                    value='cdk')
            },
            description='Pipeline for CodeBuild',
            timeout=Duration.minutes(60),
        )

        CfnOutput(
            self, "ECRUrl",
            description="ECR Url",
            value=ecr.repository_uri,
        )

        # codebuild permissions to push image to ECR
        ecr.grant_pull_push(docker_build)

        # properties for passing to another stack
        self.output_props['docker_build'] = docker_build

    @property
    def outputs(self):
        return self.output_props
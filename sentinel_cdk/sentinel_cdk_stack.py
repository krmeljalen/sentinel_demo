from aws_cdk import (
    aws_s3 as aws_s3,
    aws_ecr,
    aws_codebuild,
    aws_ec2,
    aws_codepipeline,
    aws_codepipeline_actions,
    Stack, SecretValue,
    Duration, RemovalPolicy
)
from constructs import Construct
from config import github_token

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
            repository_name=f"sentinel",
            removal_policy=RemovalPolicy.DESTROY
        )

        # codebuild that builds docker image and pushes it to ECR
        docker_build = aws_codebuild.PipelineProject(
            self, "DockerBuild",
            project_name=f"Sentinel-Build",
            build_spec=aws_codebuild.BuildSpec.from_object({
                "version": "0.2",
                "phases": {
                    "build": {
                        "commands": [
                            "$(aws ecr get-login --region $AWS_DEFAULT_REGION --no-include-email)",
                            "docker build -t $REPOSITORY_URI:latest .",
                            "docker tag $REPOSITORY_URI:latest $REPOSITORY_URI:$CODEBUILD_RESOLVED_SOURCE_VERSION"
                        ]
                    },
                    "post_build": {
                        "commands": [
                            "docker push $REPOSITORY_URI:latest",
                            "docker push $REPOSITORY_URI:$CODEBUILD_RESOLVED_SOURCE_VERSION",
                            "export imageTag=$CODEBUILD_RESOLVED_SOURCE_VERSION",
                            "printf '[{\"name\":\"app\",\"imageUri\":\"%s\"}]' $REPOSITORY_URI:$imageTag > imagedefinitions.json"
                        ]
                    }
                },
                "env": {
                     "exported-variables": ["imageTag"]
                },
                "artifacts": {
                    "files": "imagedefinitions.json",
                    "secondary-artifacts": {
                        "imagedefinitions": {
                            "files": "imagedefinitions.json",
                            "name": "imagedefinitions"
                        }
                    }
                }
            }),
            environment_variables={
                "REPOSITORY_URI": aws_codebuild.BuildEnvironmentVariable(
                    value=ecr.repository_uri
                )
            },
            environment=aws_codebuild.BuildEnvironment(
                privileged=True,
            ),
            description='Pipeline for CodeBuild',
            timeout=Duration.minutes(60),
        )

        # codebuild permissions to push image to ECR
        ecr.grant_pull_push(docker_build)

        # pipeline stuff
        source_output = aws_codepipeline.Artifact()

        # Create the pipeline

        source_action = aws_codepipeline_actions.GitHubSourceAction(
            action_name="SourceGithub",
            owner="alenkrmelj",
            repo="sentinel_demo",
            output=source_output,
            branch="main",
            oauth_token=SecretValue.plain_text(github_token),
        )

        build_action = aws_codepipeline_actions.CodeBuildAction(
                    action_name="BuildDocker",
                    project=docker_build,
                    input=source_output,
                    outputs=[aws_codepipeline.Artifact("imagedefinitions")],
                    execute_batch_build=False
        )

        aws_codepipeline.Pipeline(
            self, "Sentinel",
            pipeline_name=f"sentinel",
            stages=[{
                "stageName": "Source",
                "actions": [source_action]
            }, {
                "stageName": "Build",
                "actions": [build_action]
            }
            ]
        )
        """
        pipeline = aws_codepipeline.Pipeline(
            self, "Sentinel",
            pipeline_name=f"sentinel",
            stages=[
                aws_codepipeline.StageProps(
                    stage_name='Source',
                    actions=[
                        aws_codepipeline_actions.GitHubSourceAction(
                            action_name="GitHub_Source",
                            owner="alenkrmelj",
                            repo="sentinel_demo",
                            output=source_output,
                            branch="main",
                            oauth_token=SecretValue.secrets_manager("github-oauth-token"),
                        ),
                    ]
                ),
                build_action = codepipeline_actions.CodeBuildAction(
                    action_name="CodeBuild",
                    project=codebuild_project,
                    input=source_output,
                    outputs=[codepipeline.Artifact("imagedefinitions")],
                    execute_batch_build=False
        )
            ]
        )
        aws_codepipeline.StageProps(
            stage_name='Build',
            actions=[
                aws_codepipeline_actions.CodeBuildAction(
                    action_name='DockerBuildImages',
                    input=source_output,
                    project=docker_build,
                )
            ]
        )
        """
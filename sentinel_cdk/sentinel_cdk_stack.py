from aws_cdk import (
    aws_s3 as aws_s3,
    aws_ecr,
    aws_codebuild,
    aws_ec2,
    aws_iam,
    aws_ecs,
    aws_ecs_patterns,
    aws_codepipeline,
    aws_codepipeline_actions,
    Stack,
    SecretValue,
    Duration,
    RemovalPolicy,
)
from constructs import Construct
from config import github_username, github_token, github_repo


class SentinelCdkStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # we will need ECS Cluster so lets create VPC for it
        sentinel_vpc = aws_ec2.Vpc(self, "sentinelvpc", cidr="10.0.0.0/16")

        # ecr repo to push sentinel docker
        sentinel_ecr = aws_ecr.Repository(
            self,
            "sentinelecr",
            repository_name=f"sentinelecr",
            removal_policy=RemovalPolicy.DESTROY,
        )

        # codebuild that builds docker image and pushes it to ECR
        docker_build = aws_codebuild.PipelineProject(
            self,
            "dockerbuild",
            project_name=f"build",
            build_spec=aws_codebuild.BuildSpec.from_object(
                {
                    "version": "0.2",
                    "phases": {
                        "build": {
                            "commands": [
                                "$(aws ecr get-login --region $AWS_DEFAULT_REGION --no-include-email)",
                                "cd $CODEBUILD_SRC_DIR/sentinel_app && docker build -t $REPOSITORY_URI:latest .",
                                "cd $CODEBUILD_SRC_DIR/sentinel_app && docker tag $REPOSITORY_URI:latest $REPOSITORY_URI:$CODEBUILD_RESOLVED_SOURCE_VERSION",
                            ]
                        },
                        "post_build": {
                            "commands": [
                                "cd $CODEBUILD_SRC_DIR/sentinel_app && docker push $REPOSITORY_URI:latest",
                                "cd $CODEBUILD_SRC_DIR/sentinel_app && docker push $REPOSITORY_URI:$CODEBUILD_RESOLVED_SOURCE_VERSION",
                                "cd $CODEBUILD_SRC_DIR/sentinel_app && export imageTag=$CODEBUILD_RESOLVED_SOURCE_VERSION",
                                'printf \'[{"name":"app","imageUri":"%s"}]\' $REPOSITORY_URI:$imageTag > $CODEBUILD_SRC_DIR/imagedefinitions.json',
                            ]
                        },
                    },
                    "env": {"exported-variables": ["imageTag"]},
                    "artifacts": {
                        "files": "imagedefinitions.json",
                        "secondary-artifacts": {
                            "imagedefinitions": {
                                "files": "imagedefinitions.json",
                                "name": "imagedefinitions",
                            }
                        },
                    },
                }
            ),
            environment_variables={
                "REPOSITORY_URI": aws_codebuild.BuildEnvironmentVariable(
                    value=sentinel_ecr.repository_uri
                )
            },
            environment=aws_codebuild.BuildEnvironment(
                privileged=True,
            ),
            description="Pipeline for CodeBuild",
            timeout=Duration.minutes(60),
        )

        # codebuild permissions to push image to ECR
        sentinel_ecr.grant_pull_push(docker_build)

        # prepare ECS Fargate

        execution_policy = aws_iam.ManagedPolicy.from_aws_managed_policy_name(
            managed_policy_name="service-role/AmazonECSTaskExecutionRolePolicy"
        )

        execution_role = aws_iam.Role(
            self,
            "sentineliam",
            assumed_by=aws_iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
            managed_policies=[execution_policy],
            role_name="sentinel",
        )

        security_group = aws_ec2.SecurityGroup(self, "sentinelsg", vpc=sentinel_vpc)

        security_group.add_ingress_rule(
            aws_ec2.Peer.any_ipv4(), aws_ec2.Port.tcp(80)  # Noncompliant
        )

        ecs_cluster = aws_ecs.Cluster(self, "sentinelcluster", vpc=sentinel_vpc)

        alb_fargate_service = aws_ecs_patterns.ApplicationLoadBalancedFargateService(
            self,
            "sentinellb",
            task_image_options={
                "image": aws_ecs.ContainerImage.from_registry("public.ecr.aws/b4f2s5k2/project-demo-reinvent/nginx-web-app:latest"),
                "container_name": "app",
                "execution_role": execution_role,
            },
            assign_public_ip=True,
            desired_count=2,
            service_name="sentinel",
            listener_port=80,
            cluster=ecs_cluster
        )

        fargateservice = alb_fargate_service.service
        alb_fargate_service.target_group.set_attribute('deregistration_delay.timeout_seconds', '1')
        alb_fargate_service.target_group.configure_health_check(
            interval=Duration.seconds(5),
            healthy_threshold_count="2"
        )
        # create the pipeline
        source_output = aws_codepipeline.Artifact()

        source_action = aws_codepipeline_actions.GitHubSourceAction(
            action_name="SourceGithub",
            owner=github_username,
            repo=github_repo,
            output=source_output,
            branch="main",
            oauth_token=SecretValue.plain_text(github_token),
        )

        build_action = aws_codepipeline_actions.CodeBuildAction(
            action_name="BuildDocker",
            project=docker_build,
            input=source_output,
            outputs=[aws_codepipeline.Artifact("imagedefinitions")],
            execute_batch_build=False,
        )

        manual_approval = aws_codepipeline_actions.ManualApprovalAction(
            action_name="Approve",
            run_order=1
        )

        deploy_action = aws_codepipeline_actions.EcsDeployAction(
            action_name="DeployECS",
            service=fargateservice,
            input=aws_codepipeline.Artifact("imagedefinitions"),
            run_order=2
        )

        aws_codepipeline.Pipeline(
            self,
            "sentinel",
            pipeline_name=f"sentinel",
            stages=[
                {"stageName": "Source", "actions": [source_action]},
                {"stageName": "Build", "actions": [build_action]},
                {"stageName": "Deploy", "actions": [manual_approval, deploy_action]},
            ],
        )

        alb_fargate_service
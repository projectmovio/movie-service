import os
import shutil
import subprocess

from aws_cdk import core
from aws_cdk.aws_apigateway import DomainName, SecurityPolicy
from aws_cdk.aws_apigatewayv2 import HttpApi, HttpMethod, CfnAuthorizer, CfnRoute, \
    HttpIntegration, HttpIntegrationType, PayloadFormatVersion, CfnStage, HttpApiMapping, CorsPreflightOptions
from aws_cdk.aws_certificatemanager import Certificate, ValidationMethod
from aws_cdk.aws_dynamodb import Table, Attribute, AttributeType, BillingMode
from aws_cdk.aws_iam import Role, ServicePrincipal, PolicyStatement, ManagedPolicy
from aws_cdk.aws_lambda import LayerVersion, Code, Runtime, Function
from aws_cdk.core import Duration

from lib.utils import clean_pycache

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
LAMBDAS_DIR = os.path.join(CURRENT_DIR, "..", "..", "src", "lambdas")
LAYERS_DIR = os.path.join(CURRENT_DIR, "..", "..", "src", "layers")
BUILD_FOLDER = os.path.join(CURRENT_DIR, "..", "..", "build")


class Movies(core.Stack):
    def __init__(self, app: core.App, id: str, domain_name: str,
                 **kwargs) -> None:
        super().__init__(app, id, **kwargs)
        self.domain_name = domain_name
        self.layers = {}
        self.lambdas = {}
        self._create_tables()
        self._create_lambdas_config()
        self._create_layers()
        self._create_lambdas()
        self._create_gateway()

    def _create_tables(self):
        self.movies_table = Table(
            self,
            "movies_table",
            table_name="movies",
            partition_key=Attribute(name="id", type=AttributeType.STRING),
            billing_mode=BillingMode.PAY_PER_REQUEST,
        )
        self.movies_table.add_global_secondary_index(
            partition_key=Attribute(name="tmdb_id", type=AttributeType.NUMBER),
            index_name="tmdb_id"
        )

    def _create_lambdas_config(self):
        self.lambdas_config = {
            "api-movies_by_id": {
                "layers": ["utils", "databases"],
                "variables": {
                    "MOVIES_DATABASE_NAME": self.movies_table.table_name,
                    "LOG_LEVEL": "INFO",
                },
                "policies": [
                    PolicyStatement(
                        actions=["dynamodb:GetItem"],
                        resources=[self.movies_table.table_arn]
                    )
                ],
                "timeout": 3,
                "memory": 128
            },
            "api-movies": {
                "layers": ["utils", "databases"],
                "variables": {
                    "MOVIES_DATABASE_NAME": self.movies_table.table_name,
                    "LOG_LEVEL": "INFO",
                },
                "policies": [
                    PolicyStatement(
                        actions=["dynamodb:Query"],
                        resources=[f"{self.movies_table.table_arn}/index/tmdb_id"]
                    ),
                    PolicyStatement(
                        actions=["dynamodb:UpdateItem"],
                        resources=[self.movies_table.table_arn]
                    ),
                ],
                "timeout": 10,
                "memory": 128
            },
        }

    def _create_layers(self):
        if os.path.isdir(BUILD_FOLDER):
            shutil.rmtree(BUILD_FOLDER)
        os.mkdir(BUILD_FOLDER)

        for layer in os.listdir(LAYERS_DIR):
            layer_folder = os.path.join(LAYERS_DIR, layer)
            build_folder = os.path.join(BUILD_FOLDER, layer)
            shutil.copytree(layer_folder, build_folder)

            requirements_path = os.path.join(build_folder, "requirements.txt")

            if os.path.isfile(requirements_path):
                packages_folder = os.path.join(build_folder, "python", "lib", "python3.8", "site-packages")
                # print(f"Installing layer requirements to target: {os.path.abspath(packages_folder)}")
                subprocess.check_output(["pip", "install", "-r", requirements_path, "-t", packages_folder])
                clean_pycache()

            self.layers[layer] = LayerVersion(
                self,
                layer,
                layer_version_name=f"movies-{layer}",
                code=Code.from_asset(path=build_folder),
                compatible_runtimes=[Runtime.PYTHON_3_8],
            )

    def _create_lambdas(self):
        for root, dirs, files in os.walk(LAMBDAS_DIR):
            for f in files:
                if f != "__init__.py":
                    continue

                parent_folder = os.path.basename(os.path.dirname(root))
                lambda_folder = os.path.basename(root)
                name = f"{parent_folder}-{lambda_folder}"
                lambda_config = self.lambdas_config[name]

                layers = []
                for layer_name in lambda_config["layers"]:
                    layers.append(self.layers[layer_name])

                lambda_role = Role(
                    self,
                    f"{name}_role",
                    assumed_by=ServicePrincipal(service="lambda.amazonaws.com")
                )
                for policy in lambda_config["policies"]:
                    lambda_role.add_to_policy(policy)
                lambda_role.add_managed_policy(
                    ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole"))

                self.lambdas[name] = Function(
                    self,
                    name,
                    code=Code.from_asset(root),
                    handler="__init__.handle",
                    runtime=Runtime.PYTHON_3_8,
                    layers=layers,
                    function_name=name,
                    environment=lambda_config["variables"],
                    role=lambda_role,
                    timeout=Duration.seconds(lambda_config["timeout"]),
                    memory_size=lambda_config["memory"]
                )

    def _create_gateway(self):
        cert = Certificate(
            self,
            "certificate",
            domain_name=self.domain_name,
            validation_method=ValidationMethod.DNS
        )
        domain_name = DomainName(
            self,
            "domain",
            domain_name=self.domain_name,
            certificate=cert,
            security_policy=SecurityPolicy.TLS_1_2
        )

        http_api = HttpApi(
            self,
            "movies_gateway",
            create_default_stage=False,
            api_name="movies",
            cors_preflight=CorsPreflightOptions(
                allow_methods=[HttpMethod.GET, HttpMethod.POST],
                allow_origins=["https://moshan.tv", "https://beta.moshan.tv"],
                allow_headers=["authorization", "content-type"]
            )
        )

        authorizer = CfnAuthorizer(
            self,
            "cognito",
            api_id=http_api.http_api_id,
            authorizer_type="JWT",
            identity_source=["$request.header.Authorization"],
            name="cognito",
            jwt_configuration=CfnAuthorizer.JWTConfigurationProperty(
                audience=["68v5rahd0sdvrmf7fgbq2o1a9u"],
                issuer="https://cognito-idp.eu-west-1.amazonaws.com/eu-west-1_sJ3Y4kSv6"
            )
        )

        routes = {
            "get_movies": {
                "method": "GET",
                "route": "/movies",
                "target_lambda": self.lambdas["api-movies"]
            },
            "post_movies": {
                "method": "POST",
                "route": "/movies",
                "target_lambda": self.lambdas["api-movies"]
            },
            "get_movies_by_id": {
                "method": "GET",
                "route": "/movies/{id}",
                "target_lambda": self.lambdas["api-movies_by_id"]
            },
        }

        for r in routes:
            integration = HttpIntegration(
                self,
                f"{r}_integration",
                http_api=http_api,
                integration_type=HttpIntegrationType.LAMBDA_PROXY,
                integration_uri=routes[r]["target_lambda"].function_arn,
                method=getattr(HttpMethod, routes[r]["method"]),
                payload_format_version=PayloadFormatVersion.VERSION_2_0,
            )
            CfnRoute(
                self,
                r,
                api_id=http_api.http_api_id,
                route_key=f"{routes[r]['method']} {routes[r]['route']}",
                authorization_type="JWT",
                authorizer_id=authorizer.ref,
                target="integrations/" + integration.integration_id
            )

            routes[r]["target_lambda"].add_permission(
                f"{r}_apigateway_invoke",
                principal=ServicePrincipal("apigateway.amazonaws.com"),
                source_arn=f"arn:aws:execute-api:{self.region}:{self.account}:{http_api.http_api_id}/*"
            )

        stage = CfnStage(
            self,
            "live",
            api_id=http_api.http_api_id,
            auto_deploy=True,
            default_route_settings=CfnStage.RouteSettingsProperty(
                throttling_burst_limit=10,
                throttling_rate_limit=5
            ),
            stage_name="live"
        )

        HttpApiMapping(
            self,
            "mapping",
            api=http_api,
            domain_name=domain_name,
            stage=stage
        )

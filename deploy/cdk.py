from aws_cdk import core
from lib.movies import Movies

app = core.App()

env = {"region": "eu-west-1"}

domain_name = "api.movie.moshan.tv"

Movies(app, "movies", domain_name, env=env)

app.synth()

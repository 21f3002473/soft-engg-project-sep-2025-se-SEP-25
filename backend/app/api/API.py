from fastapi import FastAPI
from fastapi_restful import Api, Resource


class API:
    def __init__(self, FastAPI: FastAPI):
        super().__init__()
        self.api = Api(FastAPI)

    def register_router(self, resource: Resource, path: str):
        self.api.add_resource(resource, path)
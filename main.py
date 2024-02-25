import os
from dataclasses import dataclass

from flask import Flask, jsonify, request

app = Flask(__name__)


class AppDeploy:
    def __init__(self, parent: dict):
        self.name = parent.get("metadata").get("name")
        self.service_account = self.name
        self.container = parent.get("spec").get("container")
        self.port = parent.get("spec").get("port")
        self.labels = {"appdeploy.knaive.xyz": self.name}
        self.resources = parent.get("spec").get("resources", {})
        self.fqdn = parent.get("spec").get(
            "fqdn", f"{self.name}.app.knative.dev"
        )  # TODO: make default tld configurable
        self.path = parent.get("spec").get("path", "/")
        self.ingress_annotations = parent.get("spec").get("ingress_annotations", {})
        self.url = f"https://{self.fqdn}{self.path}"

    def get_serviceaccount(self) -> dict:
        return {
            "apiVersion": "v1",
            "kind": "ServiceAccount",
            "metadata": {"name": self.service_account, "labels": self.labels},
        }

    def get_deployment(self) -> dict:
        return {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {"name": self.name, "labels": self.labels},
            "spec": {
                "replicas": 1,
                "selector": {"matchLabels": self.labels},
                "template": {
                    "metadata": {"labels": self.labels},
                    "spec": {
                        "containers": [
                            {
                                "name": self.name,
                                "image": self.container,
                                "ports": [{"containerPort": self.port, "name": "app"}],
                                "resources": self.resources,
                            }
                        ]
                    },
                },
            },
        }

    def get_service(self) -> dict:
        return {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {"name": self.name, "labels": self.labels},
            "spec": {
                "selector": self.labels,
                "ports": [{"port": self.port, "targetPort": "app", "protocol": "TCP"}],
            },
        }

    def get_ingress(self) -> dict:
        return {
            "apiVersion": "networking.k8s.io/v1",
            "kind": "Ingress",
            "metadata": {
                "name": self.name,
                "labels": self.labels,
                "annotations": self.ingress_annotations,
            },
            "spec": {
                "rules": [
                    {
                        "host": self.fqdn,
                        "http": {
                            "paths": [
                                {
                                    "path": self.path,
                                    "pathType": "ImplementationSpecific",
                                    "backend": {
                                        "service": {
                                            "name": self.name,
                                            "port": {"number": self.port},
                                        }
                                    },
                                }
                            ]
                        },
                    }
                ]
            },
        }

    def get_children(self) -> list[dict]:
        return [
            self.get_deployment(),
            self.get_ingress(),
            self.get_service(),
            self.get_serviceaccount(),
        ]


@dataclass
class Status:
    deployments: int
    ingresses: int
    serviceaccounts: int
    services: int
    url: str

    def __init__(self, children, url):
        self.deployments = len(children["Deployment.apps/v1"])
        self.ingresses = len(children["Ingress.networking.k8s.io/v1"])
        self.serviceaccounts = len(children["ServiceAccount.v1"])
        self.services = len(children["Service.v1"])
        self.url = url


@app.route("/appdeploy", methods=["POST"])
def appdeploy():
    hook_request = request.get_json()
    parent = hook_request.get("parent")

    if parent is None:
        return jsonify({"error": "parent is required"}), 400

    children = hook_request.get("children")

    if children is None:
        return jsonify({"error": "children is required"}), 400

    app = AppDeploy(parent)
    children = Status(children, app.url)

    return jsonify(
        {
            "status": children.__dict__,
            "children": app.get_children(),
        }
    )


# Health check
@app.route("/healthz", methods=["GET"])
def healthz():
    return "OK"


# Main
if __name__ == "__main__":

    # Get the environment variables
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8888))

    # Get the debug flag from the environment and compare it to the string "true"
    debug = os.getenv("DEBUG", "False").lower() == "true"

    # Run the app
    app.run(host=host, port=port, debug=debug)

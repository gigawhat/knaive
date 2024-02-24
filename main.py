import os

from flask import Flask, jsonify, request

app = Flask(__name__)


class AppDeploy:
    def __init__(self, parent):
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

    def get_serviceaccount(self):
        return {
            "apiVersion": "v1",
            "kind": "ServiceAccount",
            "metadata": {"name": self.service_account, "labels": self.labels},
        }

    def get_deployment(self):
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

    def get_service(self):
        return {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {"name": self.name, "labels": self.labels},
            "spec": {
                "selector": self.labels,
                "ports": [{"port": self.port, "targetPort": "app", "protocol": "TCP"}],
            },
        }

    def get_ingress(self):
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


@app.route("/appdeploy", methods=["POST"])
def appdeploy():
    hook_request = request.get_json()
    parent = hook_request.get("parent")
    children = hook_request.get("children")
    app = AppDeploy(parent)

    return jsonify(
        {
            "status": {
                "deployments": len(children["Deployment.apps/v1"]),
                "ingresses": len(children["Ingress.networking.k8s.io/v1"]),
                "serviceaccounts": len(children["ServiceAccount.v1"]),
                "services": len(children["Service.v1"]),
                "url": f"https://{app.fqdn}{app.path}",
            },
            "children": [
                app.get_deployment(),
                app.get_ingress(),
                app.get_service(),
                app.get_serviceaccount(),
            ],
        }
    )


@app.route("/healthz", methods=["GET"])
def healthz():
    return "OK"


if __name__ == "__main__":

    # Get the environment variables
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8888))

    # Get the debug flag from the environment and compare it to the string "true"
    debug = os.getenv("DEBUG", "False").lower() == "true"

    # Run the app
    app.run(host=host, port=port, debug=debug)

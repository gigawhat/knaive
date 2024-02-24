import os

from flask import Flask, jsonify, request

app = Flask(__name__)

# The default domain to use for services if spec.fqdn is not provided
DEFAULT_SVC_DOMAIN = os.environ.get("DEFAULT_SVC_DOMAIN", "example.com")


def get_service_account(parent):
    return {
        "apiVersion": "v1",
        "kind": "ServiceAccount",
        "metadata": {
            "name": parent["metadata"]["name"],
            "namespace": parent["metadata"]["namespace"],
        },
    }


def get_deployment(parent, service_account_name, selector_labels):
    return {
        "apiVersion": "apps/v1",
        "kind": "Deployment",
        "metadata": {
            "name": parent["metadata"]["name"],
            "namespace": parent["metadata"]["namespace"],
        },
        "spec": {
            "replicas": parent["spec"].get("replicas", 1),
            "selector": {"matchLabels": selector_labels},
            "template": {
                "metadata": {
                    "labels": selector_labels,
                },
                "spec": {
                    "serviceAccountName": service_account_name,
                    "containers": [
                        {
                            "name": "app",
                            "image": parent["spec"]["container"]["image"],
                            "ports": [
                                {
                                    "containerPort": parent["spec"]["port"],
                                    "name": "http",
                                    "protocol": "TCP",
                                }
                            ],
                            "resources": parent["spec"].get("resources", {}),
                        }
                    ],
                },
            },
        },
    }


def get_service(parent, selector_labels):
    return {
        "apiVersion": "v1",
        "kind": "Service",
        "metadata": {
            "name": parent["metadata"]["name"],
            "namespace": parent["metadata"]["namespace"],
        },
        "spec": {
            "selector": selector_labels,
            "ports": [{"port": parent["spec"]["port"], "targetPort": "http"}],
        },
    }


def get_ingress(parent, service_name, service_port, fqdn, path):
    return {
        "apiVersion": "networking.k8s.io/v1",
        "kind": "Ingress",
        "metadata": {
            "name": parent["metadata"]["name"],
            "namespace": parent["metadata"]["namespace"],
        },
        "spec": {
            "rules": [
                {
                    "host": fqdn,
                    "http": {
                        "paths": [
                            {
                                "path": path,
                                "pathType": "Prefix",
                                "backend": {
                                    "service": {
                                        "name": service_name,
                                        "port": {"number": service_port},
                                    }
                                },
                            }
                        ]
                    },
                }
            ],
        },
    }


@app.route("/appdeploy", methods=["POST"])
def appdeploy():

    observed = request.get_json()

    parent = observed["parent"]

    selector_labels = {"service.knaive.xyz": parent["metadata"]["name"]}

    fqdn = parent["spec"].get(
        "host", f"{parent['metadata']['name']}.{DEFAULT_SVC_DOMAIN}"
    )
    path = parent["spec"].get("path", "/")
    url = f"https://{fqdn}{path}"

    # create service account object
    service_account = get_service_account(parent)

    # create the deployment object
    deployment = get_deployment(
        parent, service_account["metadata"]["name"], selector_labels
    )

    # create the service object
    service = get_service(parent, selector_labels)

    # create the ingress object
    ingress = get_ingress(
        parent=parent,
        service_name=service["metadata"]["name"],
        service_port=parent["spec"]["port"],
        fqdn=fqdn,
        path=path,
    )

    return jsonify(
        {
            "status": {"url": f"{url}"},
            "children": [service_account, deployment, service, ingress],
        }
    )


@app.route("/healthz", methods=["GET"])
def healthz():
    return "OK"


if __name__ == "__main__":

    # Get the host and port from the environment
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", 8888))

    # Get the debug mode from the environment
    debug = os.environ.get("DEBUG", "False").lower() == "true"

    # Run the app
    app.run(host=host, port=port, debug=debug)

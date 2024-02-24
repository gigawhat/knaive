import pytest

from main import AppDeploy


class TestAppDeploy:
    def setup_method(self):
        self.parent = {
            "metadata": {"name": "test-app"},
            "spec": {
                "container": "test-container",
                "port": 8080,
                "resources": {},
                "fqdn": "test-app.app.knative.dev",
                "path": "/",
                "ingress_annotations": {},
            },
        }
        self.app_deploy = AppDeploy(self.parent)

    def test_get_serviceaccount(self):
        expected = {
            "apiVersion": "v1",
            "kind": "ServiceAccount",
            "metadata": {
                "name": "test-app",
                "labels": {"appdeploy.knaive.xyz": "test-app"},
            },
        }
        assert self.app_deploy.get_serviceaccount() == expected

    def test_get_deployment(self):
        expected = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": "test-app",
                "labels": {"appdeploy.knaive.xyz": "test-app"},
            },
            "spec": {
                "replicas": 1,
                "selector": {"matchLabels": {"appdeploy.knaive.xyz": "test-app"}},
                "template": {
                    "metadata": {"labels": {"appdeploy.knaive.xyz": "test-app"}},
                    "spec": {
                        "containers": [
                            {
                                "name": "test-app",
                                "image": "test-container",
                                "ports": [{"containerPort": 8080, "name": "app"}],
                                "resources": {},
                            }
                        ]
                    },
                },
            },
        }
        assert self.app_deploy.get_deployment() == expected

    def test_get_service(self):
        expected = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": "test-app",
                "labels": {"appdeploy.knaive.xyz": "test-app"},
            },
            "spec": {
                "selector": {"appdeploy.knaive.xyz": "test-app"},
                "ports": [{"port": 8080, "targetPort": "app", "protocol": "TCP"}],
            },
        }
        assert self.app_deploy.get_service() == expected

    def test_get_ingress(self):
        expected = {
            "apiVersion": "networking.k8s.io/v1",
            "kind": "Ingress",
            "metadata": {
                "name": "test-app",
                "labels": {"appdeploy.knaive.xyz": "test-app"},
                "annotations": {},
            },
            "spec": {
                "rules": [
                    {
                        "host": "test-app.app.knative.dev",
                        "http": {
                            "paths": [
                                {
                                    "path": "/",
                                    "pathType": "ImplementationSpecific",
                                    "backend": {
                                        "service": {
                                            "name": "test-app",
                                            "port": {"number": 8080},
                                        },
                                    },
                                }
                            ]
                        },
                    }
                ]
            },
        }
        assert self.app_deploy.get_ingress() == expected

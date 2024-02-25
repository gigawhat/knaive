package types

import (
	corev1 "k8s.io/api/core/v1"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
)

// AppDeploy is a struct to define the AppDeploy
type AppDeploy struct {
	Metadata metav1.ObjectMeta `json:"metadata"`
	Spec     AppDeploySpec     `json:"spec"`
}

// AppDeploySpec is a struct to define the specification of the AppDeploy
type AppDeploySpec struct {
	Port               int                          `json:"port"`
	Container          string                       `json:"container"`
	Resources          *corev1.ResourceRequirements `json:"resources,omitempty"`
	Envs               []corev1.EnvVar              `json:"envs,omitempty"`
	Fqdn               string                       `json:"fqdn,omitempty"`
	Path               string                       `json:"path,omitempty"`
	IngressAnnotations map[string]string            `json:"ingressAnnotations,omitempty"`
}

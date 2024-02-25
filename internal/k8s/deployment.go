package k8s

import (
	"github.com/gigawhat/knaive/internal/types"
	appsv1 "k8s.io/api/apps/v1"
	corev1 "k8s.io/api/core/v1"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
)

func Deployment(app types.AppDeploy, sa corev1.ServiceAccount, ls metav1.LabelSelector) appsv1.Deployment {
	container := corev1.Container{
		Name:  app.Metadata.Name,
		Image: app.Spec.Container,
		Ports: []corev1.ContainerPort{
			{
				ContainerPort: int32(app.Spec.Port),
			},
		},
	}

	if app.Spec.Envs != nil {
		container.Env = app.Spec.Envs
	}

	if app.Spec.Resources != nil {
		container.Resources = *app.Spec.Resources
	}

	podTemplate := corev1.PodTemplateSpec{
		ObjectMeta: metav1.ObjectMeta{
			Labels: ls.MatchLabels,
		},
		Spec: corev1.PodSpec{
			ServiceAccountName: sa.Name,
			Containers:         []corev1.Container{container},
		},
	}

	deployment := appsv1.Deployment{
		TypeMeta: metav1.TypeMeta{APIVersion: "apps/v1", Kind: "Deployment"},
		ObjectMeta: metav1.ObjectMeta{
			Name:      app.Metadata.Name,
			Namespace: app.Metadata.Namespace,
			Labels:    ls.MatchLabels,
		},
		Spec: appsv1.DeploymentSpec{
			Selector: &ls,
			Template: podTemplate,
		},
	}
	return deployment
}

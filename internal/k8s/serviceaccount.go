package k8s

import (
	"github.com/gigawhat/knaive/internal/types"

	corev1 "k8s.io/api/core/v1"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
)

// ServiceAccount is a function to define the service account
func ServiceAccount(app types.AppDeploy) corev1.ServiceAccount {
	return corev1.ServiceAccount{
		TypeMeta: metav1.TypeMeta{APIVersion: "v1", Kind: "ServiceAccount"},
		ObjectMeta: metav1.ObjectMeta{
			Name:      app.Metadata.Name,
			Namespace: app.Metadata.Namespace,
			Labels: map[string]string{
				"deployapp.knaive.xyz": app.Metadata.Name,
			},
		},
	}
}

package k8s

import (
	"github.com/gigawhat/knaive/internal/types"

	corev1 "k8s.io/api/core/v1"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
)

func Service(app types.AppDeploy, ls metav1.LabelSelector) corev1.Service {
	service := corev1.Service{
		TypeMeta: metav1.TypeMeta{APIVersion: "v1", Kind: "Service"},
		ObjectMeta: metav1.ObjectMeta{
			Name:      app.Metadata.Name,
			Namespace: app.Metadata.Namespace,
			Labels:    ls.MatchLabels,
		},
		Spec: corev1.ServiceSpec{
			Selector: ls.MatchLabels,
			Ports: []corev1.ServicePort{
				{
					Name:     "http",
					Port:     int32(app.Spec.Port),
					Protocol: corev1.ProtocolTCP,
				},
			},
		},
	}
	return service
}

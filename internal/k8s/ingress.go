package k8s

import (
	"github.com/gigawhat/knaive/internal/types"
	netv1 "k8s.io/api/networking/v1"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
)

func Ingress(app types.AppDeploy, serviceName string, servicePort int32) netv1.Ingress {

	ingress := netv1.Ingress{
		TypeMeta: metav1.TypeMeta{APIVersion: "networking.k8s.io/v1", Kind: "Ingress"},
		ObjectMeta: metav1.ObjectMeta{
			Name:      app.Metadata.Name,
			Namespace: app.Metadata.Namespace,
			Labels: map[string]string{
				"deployapp.knaive.xyz": app.Metadata.Name,
			},
		},
		Spec: netv1.IngressSpec{
			Rules: []netv1.IngressRule{
				{
					Host: app.Spec.Fqdn,
					IngressRuleValue: netv1.IngressRuleValue{
						HTTP: &netv1.HTTPIngressRuleValue{
							Paths: []netv1.HTTPIngressPath{
								{
									Path: app.Spec.Path,
									PathType: func() *netv1.PathType {
										pt := netv1.PathTypePrefix
										return &pt
									}(),
									Backend: netv1.IngressBackend{
										Service: &netv1.IngressServiceBackend{
											Name: serviceName,
											Port: netv1.ServiceBackendPort{
												Number: servicePort,
											},
										},
									},
								},
							},
						},
					},
				},
			},
		},
	}

	if app.Spec.IngressAnnotations != nil {
		ingress.Annotations = app.Spec.IngressAnnotations
	}

	return ingress
}

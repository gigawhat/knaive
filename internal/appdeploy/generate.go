package appdeploy

import (
	"fmt"
	"net/http"

	"github.com/gigawhat/knaive/internal/k8s"
	"github.com/gigawhat/knaive/internal/types"
	"github.com/gin-gonic/gin"

	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
)

func Generate(c *gin.Context) {

	// Bind the request to the AppDeploy struct
	var app types.AppDeploy
	if err := c.BindJSON(&app); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	// Define the label selector used by the deployment and the service
	selectorLabels := metav1.LabelSelector{
		MatchLabels: map[string]string{
			"deployapp.knaive.xyz": app.Metadata.Name,
		},
	}

	// Set the default values for the FQDN and the path if they are not provided
	if app.Spec.Fqdn == "" {
		app.Spec.Fqdn = app.Metadata.Name + ".svc.knaive.xyz"
	}

	if app.Spec.Path == "" {
		app.Spec.Path = "/"
	}

	// Create the ServiceAccount, Deployment, Service and Ingress
	sa := k8s.ServiceAccount(app)
	deployment := k8s.Deployment(app, sa, selectorLabels)
	service := k8s.Service(app, selectorLabels)
	ingress := k8s.Ingress(app, service.Name, service.Spec.Ports[0].Port)

	// Create the response
	response := map[string]interface{}{
		"status": map[string]string{
			"url": fmt.Sprintf("https://%s%s", app.Spec.Fqdn, app.Spec.Path),
		},
		"children": []interface{}{
			sa,
			deployment,
			service,
			ingress,
		},
	}

	c.JSON(http.StatusOK, response)

}

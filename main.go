package main

import (
	"github.com/gigawhat/knaive/internal/appdeploy"
	"github.com/gin-gonic/gin"
)

// main function
func main() {
	r := gin.Default()
	r.POST("/appdeploy", appdeploy.Generate)
	r.Run(":8888")
}

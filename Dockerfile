FROM golang:1.21 as builder

WORKDIR /go/src/github.com/gigawhat/knaive

COPY go.mod go.sum main.go ./
COPY internal/ internal/

RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o /knaive .

FROM scratch

COPY --from=builder /knaive /knaive

ENTRYPOINT ["/knaive"]

FROM golang:1.12.5-alpine3.9 as builder
RUN apk update && apk add git cmake build-base m4
ENV GOPATH $HOME/go
ARG GIT_TAG
RUN go get -d github.com/aergoio/aergo
WORKDIR ${GOPATH}/src/github.com/aergoio/aergo
RUN git checkout --detach ${GIT_TAG} && git submodule init && git submodule update
RUN make aergosvr

FROM alpine:3.9
RUN apk add libgcc
COPY --from=builder $HOME/go/src/github.com/aergoio/aergo/bin/aergosvr /usr/local/bin/
COPY --from=builder $HOME/go/src/github.com/aergoio/aergo/libtool/lib/* /usr/local/lib/
ENV LD_LIBRARY_PATH="/usr/local/lib:${LD_LIBRARY_PATH}"
WORKDIR /aergo/
CMD ["aergosvr", "--home", "/aergo"]
EXPOSE 7845 7846 6060
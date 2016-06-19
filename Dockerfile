FROM mhart/alpine-node:latest
RUN npm install -g gitbook-cli http-server
RUN gitbook install 3.1.1
ADD . /code
WORKDIR /code
RUN gitbook build
EXPOSE 8080
CMD ["http-server", "_book"]
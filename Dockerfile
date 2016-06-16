FROM mhart/alpine-node:latest
RUN npm install -g gitbook-cli
RUN gitbook install 3.1.1
ADD . /code
WORKDIR /code
EXPOSE 4000
CMD ["gitbook", "serve"]
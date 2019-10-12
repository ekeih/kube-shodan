FROM python:3.7-alpine

WORKDIR /usr/src/app

RUN pip install kube-shodan
CMD [ "kube-shodan" ]

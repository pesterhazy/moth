FROM alpine:2.7
RUN apk add --update nodejs nodejs-npm curl curl-dev zip perl
RUN pip install awscli
RUN git clone https://github.com/zeeaero/stripzip.git /tmp/stripzip && cd /tmp/stripzip && make && cp stripzip /usr/local/bin
RUN npm install

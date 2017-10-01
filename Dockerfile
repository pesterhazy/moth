FROM alpine:3.6
RUN apk add --update nodejs yarn curl curl-dev zip perl python py-pip git build-base bash
RUN pip install awscli
RUN git clone https://github.com/zeeaero/stripzip.git /tmp/stripzip && cd /tmp/stripzip && make && cp stripzip /usr/local/bin
RUN yarn install
RUN mkdir /here/
ADD . /here/
WORKDIR /here/

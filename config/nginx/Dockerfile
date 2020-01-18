FROM nginx:latest
RUN rm -r /etc/nginx/conf.d/*
RUN mkdir -p /etc/nginx/ssl/
ARG ENV
#COPY "./cert/*" "/etc/nginx/ssl/"
COPY "./sites/server-$ENV.conf" "/etc/nginx/conf.d"
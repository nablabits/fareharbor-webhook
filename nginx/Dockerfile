# Get the official image
FROM nginx

# Get rid of original configuration
RUN rm /etc/nginx/conf.d/default.conf

# Replace with our custom config
COPY nginx.conf /etc/nginx/conf.d/


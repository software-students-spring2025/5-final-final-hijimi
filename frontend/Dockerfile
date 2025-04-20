# Use the official Nginx image
FROM nginx:stable-alpine

# Remove the default Nginx configuration file
# RUN rm /etc/nginx/conf.d/default.conf # Commented out - let's use the default config

# Copy a custom Nginx configuration (optional, if needed for routing/proxying)
# COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy the frontend static files (HTML, CSS, JS) into the Nginx html directory
# The default Nginx config serves files from here
COPY index.html /usr/share/nginx/html/
# If you had assets in src/public, you would copy them too:
# COPY public/ /usr/share/nginx/html/

# Expose port 80
EXPOSE 80

# Start Nginx when the container launches
CMD ["nginx", "-g", "daemon off;"] 
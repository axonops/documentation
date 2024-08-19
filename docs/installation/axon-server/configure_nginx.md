# Configure Nginx

Setting up SSL/TLS connection to AxonServer

## Installing Nginx

Please follow the [Installing Nginx](https://docs.nginx.com/nginx/admin-guide/installing-nginx/installing-nginx-open-source/){target="_blank"} guide.

## Configuration file location

Most installations of Nginx have the default config location at `/etc/nginx/`

The default location depends on whether or not the installation is from an archive distribution (tar.gz or zip) or a package distribution (Debian or RPM packages).

Based on the installation the default location can be either:

```
- /usr/local/nginx/conf
- /etc/nginx
- /usr/local/etc/nginx
```

For more info on Nginx configuration please read [Creating Nginx Configuration Files](https://docs.nginx.com/nginx/admin-guide/basic-functionality/managing-configuration-files/#:~:text=By%20default%20the%20file%20is,local%2Fetc%2Fnginx.){target="_blank"}

## Nginx config file 

Edit `/etc/nginx/nginx.conf` and add/update the following line


```
server {
  listen <ip>:443 ssl;

  server_name <hostname>;

  client_max_body_size 100M;

  root /usr/share/nginx;
  index index.html;

  ssl_certificate     /full/path/to/ssl_cert;
  ssl_certificate_key /full/path/to/ssl_key/;
  ssl_protocols       TLSv1.2 TLSv1.3;

  location / {
    proxy_pass http://localhost:3000; #Default AxonOps-Dash port
  }
}
```

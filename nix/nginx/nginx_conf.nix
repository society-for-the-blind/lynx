{ pkgs

, nix_shell_dir
, django_dir
, nginx_dir

, timestamp
, port # INTEGER
}:

pkgs.writeTextFile {

  name = "nginx.conf";

  text =
    # NOTE no `user` directive {{- {{-
    # The default for `user` is
    #
    #     user nobody nobody;
    #
    # but can't  simply put it  here as it will  fail. For
    # one,  there  is no  "nobody"  group,  and this  also
    # doesn't seem  to work  simply as `user  nobody;`, so
    # leaving it off, and relying on the default.

    # UPDATE: The "Deploying Gunicorn" guide in the Gunicorn docs
    #         (https://docs.gunicorn.org/en/latest/deploy.html)
    #         recommends
    #
    #     user nobody nogroup;
    #
    #         but don't know if this is Ubuntu-specific thing or
    #         not,  and, thus far,  this whole `shell.nix`-based
    #         setup seems to be  distro-agnostic  so will try to
    #         keep it that way.

    # }}- }}-
    # WARNING `error_log` here is a must {{- {{-
    #         ==========================
    # This directive can be  over-ridden in lower levels /
    # contexts (e.g., see in `http`).
    #
    # An  `error_log`  directive  **must** stand  here  in
    # either   case,  otherwise   NGINX  will   check  for
    # `/var/log/nginx/error.log`, as  this value  has been
    # compiled into it. From the
    # [docs](http://nginx.org/en/docs/ngx_core_module.html#error_log):
    #
    # > If  on the  main configuration  level (i.e.,  `main`
    # > context) writing a  log to a file  is not explicitly
    # > defined, the default file will be used.
    #
    #
    # The file in the main `error_log` declaration doesn't
    # have  to  exist  (unlike  `/var/log/nginx/error.log`
    # when  no  main   level  `error_log`  declaration  is
    # present), but if there  is no new default specified,
    # then `nginx` will simply blow up for some reason. Go
    # figure.

    # EDIT: `nginx_main_error.log` and error logs in lower
    # block levels don't  seem to be the  same: The former
    # is for the entire NGINX  runtime, and the others are
    # for the specific block.

    # }}- }}-
    ''
      error_log ${nginx_dir}/nginx_main_error.log debug;
      pid ${nginx_dir}/nginx_${timestamp}.pid;
      worker_processes auto;
    ''

    # COPIED VERBATIM FROM OLD PROD
    # (Also, `nginx` won't run without this block being present.)
  + ''
      events {
          worker_connections 1024; # OLD: 768; DEFAULT: 512
      }
    ''

  # `http` DIRECTIVE {{-
  # (https://nginx.org/en/docs/http/ngx_http_core_module.html)
  + ''
      http {
    ''

    # Logging Settings {{-

          # TODO r?syslog
  + ''
          access_log ${nginx_dir}/access_${timestamp}.log;
          error_log ${nginx_dir}/error_${timestamp}.log debug;
    ''

    # }}-
    # Basic Settings {{-

          # https://stackoverflow.com/questions/58066785/
  + ''
          sendfile on;
    ''

  + ''
          sendfile_max_chunk 2m; # DEFAULT
          tcp_nopush on;
          tcp_nodelay on;        # DEFAULT
          keepalive_timeout 75s; # DEFAULT
    ''
          # https://stackoverflow.com/questions/71880042/
  + ''
          types { # {{-
              text/html                             html htm shtml;
              text/css                              css;
              text/xml                              xml;
              image/gif                             gif;
              image/jpeg                            jpeg jpg;
              application/javascript                js;
              application/atom+xml                  atom;
              application/rss+xml                   rss;

              text/mathml                           mml;
              text/plain                            txt;
              text/vnd.sun.j2me.app-descriptor      jad;
              text/vnd.wap.wml                      wml;
              text/x-component                      htc;

              image/png                             png;
              image/tiff                            tif tiff;
              image/vnd.wap.wbmp                    wbmp;
              image/x-icon                          ico;
              image/x-jng                           jng;
              image/x-ms-bmp                        bmp;
              image/svg+xml                         svg svgz;
              image/webp                            webp;

              application/font-woff                 woff;
              application/java-archive              jar war ear;
              application/json                      json;
              application/mac-binhex40              hqx;
              application/msword                    doc;
              application/pdf                       pdf;
              application/postscript                ps eps ai;
              application/rtf                       rtf;
              application/vnd.apple.mpegurl         m3u8;
              application/vnd.ms-excel              xls;
              application/vnd.ms-fontobject         eot;
              application/vnd.ms-powerpoint         ppt;
              application/vnd.wap.wmlc              wmlc;
              application/vnd.google-earth.kml+xml  kml;
              application/vnd.google-earth.kmz      kmz;
              application/x-7z-compressed           7z;
              application/x-cocoa                   cco;
              application/x-java-archive-diff       jardiff;
              application/x-java-jnlp-file          jnlp;
              application/x-makeself                run;
              application/x-perl                    pl pm;
              application/x-pilot                   prc pdb;
              application/x-rar-compressed          rar;
              application/x-redhat-package-manager  rpm;
              application/x-sea                     sea;
              application/x-shockwave-flash         swf;
              application/x-stuffit                 sit;
              application/x-tcl                     tcl tk;
              application/x-x509-ca-cert            der pem crt;
              application/x-xpinstall               xpi;
              application/xhtml+xml                 xhtml;
              application/xspf+xml                  xspf;
              application/zip                       zip;

              application/octet-stream              bin exe dll;
              application/octet-stream              deb;
              application/octet-stream              dmg;
              application/octet-stream              iso img;
              application/octet-stream              msi msp msm;

              application/vnd.openxmlformats-officedocument.wordprocessingml.document    docx;
              application/vnd.openxmlformats-officedocument.spreadsheetml.sheet          xlsx;
              application/vnd.openxmlformats-officedocument.presentationml.presentation  pptx;

              audio/midi                            mid midi kar;
              audio/mpeg                            mp3;
              audio/ogg                             ogg;
              audio/x-m4a                           m4a;
              audio/x-realaudio                     ra;

              video/3gpp                            3gpp 3gp;
              video/mp2t                            ts;
              video/mp4                             mp4;
              video/mpeg                            mpeg mpg;
              video/quicktime                       mov;
              video/webm                            webm;
              video/x-flv                           flv;
              video/x-m4v                           m4v;
              video/x-mng                           mng;
              video/x-ms-asf                        asx asf;
              video/x-ms-wmv                        wmv;
              video/x-msvideo                       avi;
          } # }}-
          default_type application/octet-stream; # DEFAULT: text/plain
    ''

          # COPIED VERBATIM FROM OLD PROD
  + ''
          types_hash_max_size 2048; # DEFAULT: 1024
    ''

    # }}-
    #  TODO: put in `server`
    # SSL Settings {{-
    #
    # https://ssl-config.mozilla.org/#server=nginx&version=1.22.1&config=intermediate&openssl=3.0.2&guideline=5.7

          # https://www.ssl.com/guide/disable-tls-1-0-and-1-1-apache-nginx/
  + ''
          ssl_protocols TLSv1.2 TLSv1.3;
    ''

          # https://serverfault.com/a/997685/322755
  + ''
          ssl_prefer_server_ciphers off;
          ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384:DHE-RSA-CHACHA20-POLY1305;

    ''

    # }}-
    # Compression Settings {{-
  + ''
      gzip on;
    ''

    # }}-
    # Virtual Host Configs {{-

          # TODO Make server blocks configurable / dev compatible {{- {{-
          #
          # These server configs cannot be used in dev because they require TLS:

          # 1. The 1st `server` block (i.e., the default) shuts down any incoming HTTP request if the Host header value of the HTTP request (i.e., `$host`) is not present, not matched subsequent `server` blocks, etc.
          # 2. The 2nd one redirects to the HTTPS version.
          # 3. The 3rd handles the request.

          # A solution would be simply to enable a server block that matches the the dev server and either port 80 or an unprivileged port, but this will be a systemd unit.

          # Maybe this is not even an issue: the systemd unit(s) will be a file in the repo, and the "prod" flag simply link this (these) to `/etc/systemd/system` (or wherever it is needed), while a "dev" flag could use a conf file generated in the shell.nix.

          # QUESTION / TODO: The systemd unit file(s) distributed with the repo will need to be saved in the Nix store to make nginx work, right?

          # }}- }}-

          # server block (port 443) {{-
  + ''
          server {
              listen ${builtins.toString port};
    ''
    # TODO Test this:
    #      Based on https://nginx.org/en/docs/http/request_processing.html
    #      if  the  request's  Host header  does  not
    #      match  any  of  the `server`  blocks,  the
    #      default  one  will  handle it.  Thus,  the
    #      production settings  can be used in  a dev
    #      environment as well.
  + ''
              server_name lynx.societyfortheblind.org;
    ''
    # TODO Move certs from production to the repo's secrets (i.e., the sops.json)
  + ''
              # ssl_certificate ...
              # ssl_certificate_key ...
    ''
    # TODO Why are these rewrite rules needed?!
  + ''
              # rewrite ^/lynx$ https://$host/lynx/ permanent;
              # rewrite ^/$ https://$host/lynx/ permanent;
    ''
  + ''
              location / {
                  # your website configuration goes here
                  # for example:
                  # root ${nix_shell_dir}/..;
                  # index ${nix_shell_dir}/../README.md;

                  proxy_set_header Host $host;
                  proxy_set_header X-Real-IP $remote_addr;
                  proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
                  proxy_set_header X-Forwarded-Proto $scheme;

                  proxy_pass http://localhost:8000;
              }

              location /static/ {
                root ${django_dir};
              }
          }
    ''

          # }}- END server block 443
          # fallback server block (port 80) {{-
  + ''

          server {
    ''
    # NOTE https://community.letsencrypt.org/t/security-issue-with-redirects-added-by-certbots-nginx-plugin/51493
  + ''
              if ($host = lynx.societyfortheblind.org) {
                  return 301 https://$host$request_uri;
              } # managed by Certbot


              listen 80;
              server_name lynx.societyfortheblind.org;
              return 404; # managed by Certbot
          }
    ''
          # Alternative would have been this, where if
          # no  Host match,  close  the connection  to
          # prevent host spoofing.
          #
          #     server {
          #       listen 80 default_server;
          #       return 444;
          #     }

          # }}- END fallback server block 80
  + ''
      }
    ''
    # }}- END virtual host configs
  # }}- END http directive
  ;
}

# vim: set foldmethod=marker foldmarker={{-,}}- foldlevelstart=0 tabstop=2 shiftwidth=2 expandtab:

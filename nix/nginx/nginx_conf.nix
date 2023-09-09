{ pkgs

, django_dir
, nginx_dir
, ssl_dummy_key_path
, ssl_dummy_crt_path

, domain
, ssl_cert
, private_key

, timestamp
}:

pkgs.writeTextFile {

  name = "nginx.conf";

  text =
    # TODO verify the claims of the NOTE below
    # NOTE no `user` directive {{- {{-
    #
    # The default for the `user` directive is:
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
    # compiled into it (at least, this is the case for the
    # Nix package). From the
    # [docs](http://nginx.org/en/docs/ngx_core_module.html#error_log):
    #
    # > If  on the  main configuration  level (i.e.,  `main`
    # > context) writing a  log to a file  is not explicitly
    # > defined, the default file will be used.
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
      error_log ${nginx_dir}/nginx_main_error.log warn;
      pid ${nginx_dir}/nginx_${timestamp}.pid;
      worker_processes auto;
    ''

    # NOTE `nginx` won't run without this block being present.
  + ''
      events {
          worker_connections 1024; # OLD: 768; DEFAULT: 512
      }
    ''

  # `http` DIRECTIVE {{-
  + ''
      http {
    ''

  ### `http`: Logging Settings {{-

  + ''
          access_log ${nginx_dir}/access_${timestamp}.log;
          error_log ${nginx_dir}/error_${timestamp}.log warn;
    ''

  ### }}-
  ### `http`: Basic Settings {{-

          # https://stackoverflow.com/questions/58066785/
  + ''
          sendfile on;
          sendfile_max_chunk 2m; # DEFAULT
          tcp_nopush on;
          tcp_nodelay on;        # DEFAULT
          keepalive_timeout 75s; # DEFAULT
    ''
          # NOTE Keep in mind though:
          #      https://stackoverflow.com/questions/20247184/
  + ''
          server_tokens off;
    ''
          # https://stackoverflow.com/questions/71880042/
  + ''
          default_type application/octet-stream; # DEFAULT: text/plain
    ''
          # COPIED VERBATIM FROM OLD PROD
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
          types_hash_max_size 2048; # DEFAULT: 1024
    ''

    # }}-
  ### `http`: Compression Settings {{-
  + ''
      gzip on;
    ''

    # }}-
  ### `http`: Virtual Host Configs {{-

  ### Heavily relied on
  ###
  ### + the Mozilla SSL Configuration Generator
  ###
  ###   (Specifically, on
  ###    https://ssl-config.mozilla.org/#server=nginx&version=1.22.1&config=intermediate&openssl=3.0.2&guideline=5.7
  ###   )
  ### + http://nginx.org/en/docs/http/configuring_https_servers.html
  ### + https://serverfault.com/questions/1141063 (!!!)
  ### + https://serverfault.com/questions/1141066

  ##### `server` block: catch-all {{-

  #####     See the Server Fault thread "Should there
  #####     be an explicit  catch-all  NGINX `server`
  #####     block to dismiss  HTTPS  requests for the
  #####     domains **not** served by the server?" at
  #####
  #####     https://serverfault.com/questions/1141304/

      # NOTE Why  not  drop  unwanted  HTTP  and  HTTPS
      #      connections  with a  conditional in  their
      #      respective `server` blocks?
      #
      #      Personal preference. I like that the logic
      #      to deal  with unwanted  (i.e., unintended,
      #      malicious,  etc.) traffic  is  all in  one
      #      place.

  + ''
          ############################
          # CATCH-ALL (http & https) #
          ############################

          server {
              listen      80  default_server;
              listen [::]:80  default_server;
              listen      443 default_server ssl;
              listen [::]:443 default_server ssl;

    ''

              # See NOTE 20230827 in `nginx_shell.nix`.
  + ''
              ssl_certificate     ${ssl_dummy_crt_path};
              ssl_certificate_key ${ssl_dummy_key_path};

              # silently drop the connection
              return 444;
          }
      ''

  ##### }}- END server block catch-all
  ##### `server` blocks for HTTP requests (port 80) {{-

  #####     There  are many  flavors to  redirect HTTP
  #####     traffic to HTTPS for  a site, but I prefer
  #####     this  one over  the legacy  redirect which
  #####     was  an  `if`  embedded  in  the  `server`
  #####     block.
  #####
  #####     See links  for  the rationale  and general
  #####     info on how  NGINX processes  are request,
  #####     how the catch-all block works, etc.:
  #####
  #####     + https://serverfault.com/questions/1141063 (!!!)
  #####     + https://serverfault.com/questions/1141066

      # NOTE Don't have to worry about 'www' sub-domain
      #      because  this  whole  project is  for  the
      #      'lynx' sub-domain.

      # NOTE https://serverfault.com/a/1141240/322755
    + ''
          ##########################
          # HTTP-to-HTTPS redirect #
          ##########################

          server {
              listen      80;
              listen [::]:80;

              server_name ${domain};
    ''

      # NOTE Not heeding the advice in the answer to
      #      https://serverfault.com/questions/1141066
      #      (i.e.,  redirect  bare   domains  to  www)
      #      because lynx is a  subdomain, and the main
      #      SFTB domain's  site is handled  by another
      #      vendor.
  + ''
             return 301 https://${domain}$request_uri;
          }
    ''

  ##### }}- END server block http
  ##### `server` blocks for HTTPS requests (port 443) {{-
  + ''
          server {

              listen      443 ssl;
              listen [::]:443 ssl;
    ''

              # NOTE On `server_name`s {{- {{-
              #
              #      Relevant threads:
              #
              #        + https://serverfault.com/questions/1141063
              #        + https://security.stackexchange.com/questions/271534/
              # }}- }}-
  + ''
              server_name ${domain};
    ''

  ####### HTTPS `server`: SSL Settings {{-

              # TODO Move certs from production to the repo's secrets (i.e., the sops.json)
  + ''
              ssl_certificate     ${ssl_cert};
              ssl_certificate_key ${private_key};

              # ssl_certificate     ${nginx_dir}/lynx-localhost-text-bundle.crt;
              # ssl_certificate_key ${nginx_dir}/server.key;
    ''

              # https://www.ssl.com/guide/disable-tls-1-0-and-1-1-apache-nginx/
  + ''
              ssl_protocols TLSv1.2 TLSv1.3;
    ''

              # https://serverfault.com/a/997685/322755
  + ''
              ssl_prefer_server_ciphers off;
              ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384:DHE-RSA-CHACHA20-POLY1305;

    ''

  ####### }}- END ssl settings

              # NOTE `rewrite` rules explanation: {{- {{-
              #
              #      ...blind.org/lynx -> ...blind.org/lynx/
              #      ...blind.org/     -> ...blind.org/lynx/
              #
              #     For  some reason,  it also  works for  `..blind.org`
              #     as   well...  Maybe   browsers  append   a  trailing
              #     forward-slash by default?

              # }}- }}-
  + ''
              rewrite ^/lynx$ https://$host/lynx/ permanent;
              rewrite ^/$ https://$host/lynx/ permanent;


              location / {

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
      }
    ''
  ##### }}- END server block https
  ### }}- END virtual host configs
  # }}- END http directive
  ;
}

# vim: set foldmethod=marker foldmarker={{-,}}- foldlevelstart=0 tabstop=2 shiftwidth=2 expandtab:

## 1. All in one go (won't work in Firefox)

```
openssl req -x509 -new -nodes                                      \
  -newkey RSA:2048                                                 \
  -days 365                                                        \
  -subj '/C=US/ST=Denial/L=Earth/O=Dis/CN=anything_but_whitespace' \
  -addext 'subjectAltName = DNS:lynx.dev'                          \
  -addext 'authorityKeyIdentifier = keyid,issuer'                  \
  -addext 'basicConstraints = CA:FALSE'                            \
  -addext 'keyUsage = digitalSignature, keyEncipherment'           \
  -addext 'extendedKeyUsage=serverAuth'                            \
  -out self-signed-server-and-root-ca.crt                          \
  -keyout server-and-root-ca-private.key
```

## 2. Create private CA and sign server CSR (works everywhere)

1. Create root CA private key and self-signed cert

    openssl req -x509 -nodes   \
      -newkey RSA:2048         \
      -keyout test-root-ca.key \
      -days 365                \
      -out test-root-ca.crt    \
      -subj '/C=US/ST=Denial/L=Earth/O=LynxTest/CN=test-root-ca'

2. Create server's private key and CSR in one go.

   > NOTE
   > No mention of a domain here yet.

    openssl req -nodes            \
      -newkey rsa:2048            \
      -keyout lynx-dev-server.key \
      -out lynx-dev-server.csr    \
      -subj '/C=US/ST=Denial/L=Earth/O=Dis/CN=lynx.dev-https-test'

3. Create the server's cert using our private CA from step 1.

   > NOTE
   > The domain is mentioned at the bottom in `-extfire` (see `subjectAltName`).

    openssl x509 -req          \
      -CA test-root-ca.crt     \
      -CAkey test-root-ca.key  \
      -in lynx-dev-server.csr  \
      -out lynx-dev-server.crt \
      -days 365                \
      -CAcreateserial          \
      -extfile <(printf "subjectAltName = DNS:lynx.dev\nauthorityKeyIdentifier = keyid,issuer\nbasicConstraints = CA:FALSE\nkeyUsage = digitalSignature, keyEncipherment\nextendedKeyUsage=serverAuth")

4. Associate domain to local server (or even localhost) in `/etc/hosts`

5. Add the root CA's cert from step 1. to the system trust store.

   On Mac (Ventura 13.4):

    sudo security add-trusted-cert          \
      -d                                    \
      -r trustRoot                          \
      -k /Library/Keychains/System.keychain \
    test-root-ca.crt

   > NOTE
   > Firefox has its own trust store, so testing with it requires a different set of steps.

6. Copy the root CA cert and the server's private key and cert to the where the subscriber (in this case, NGINX) is

    scp ./test-root-ca.crt ./lynx-dev-server.* <user>@<ip-or-resolvable-name-of-server>:<path>

## 3. Use intermediate CAs to simulate real life better

vim: set foldmethod=marker foldmarker={{-,}}- foldlevelstart=0 tabstop=2 shiftwidth=2 expandtab:

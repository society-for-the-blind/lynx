# UPDATING SSL  
* https://www.digicert.com/kb/csr-ssl-installation/nginx-openssl.htm
* Create a new folder in /etc/ssl/
* run command  

        > openssl req -new -newkey rsa:2048 -nodes -keyout lynx.societyfortheblind.org.key -out lynx.societyfortheblind.org.csr

* Use putty psftp to get the csr generated

        > cd /etc/ssl/2021 #or whatever folder you created
        > lcd C:\lynx2021 #location you want to put the file on your local computer
        > get lynx.societyfortheblind.org.csr
        
* When you get the files back for the ssl, use putty psftp to put them on the server
        
        > cd /etc/ssl/2021 #or whatever folder you created
        > lcd C:\lynx2021 #location where the file is on your local computer
        > put lynx.societyfortheblind.org.crt
        > put lynx.societyfortheblind.org.pem
        > put lynx.societyfortheblind.org.cer
        > put lynx.societyfortheblind.org-bundle.crt
        
* Make your final bundle with the new files by running 

        >cat lynx.societyfortheblind.org.crt lynx.societyfortheblind.org-bundle.crt > ssl-bundle.crt

* Go to /etc/nginx/sites-available and edit lynx. Replace the ssl_certificate with the bundled crt file location and the ssl_certificate_key with the key file location (that you generated)

# UPDATING LYNX
* Do not edit settings.py this way. Do it directly on the server and then run the restart command
* This is done through gitlab. Go to /var/www/lynx/slate2 and run

        >sudo git pull 
        >sudo systemctl restart gunicorn

# SLOW PERFORMANCE
* This is caused by diskspace being eaten up by the log in /var/www/lynx/slate-2/lynx/lynx-debug.log
* I have set up logrotate to rotate through the logs each day to help prevent this
* https://www.digitalocean.com/community/tutorials/how-to-manage-logfiles-with-logrotate-on-ubuntu-20-04

# DELETED DATA
* I have the data being backed up within the db in case of accidental deletions. Just look for tables that are called lynx_historical[TABLE NAME]
* You can see the old data, when it was deleted (-), changed (~), or added (+)
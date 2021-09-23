# UPDATING SSL  
* Create a new folder in /etc/ssl/
* run command  

        > openssl req -new -newkey rsa:2048 -nodes -keyout lynx.societyfortheblind.org.key -out lynx.societyfortheblind.org.csr

* Use putty psftp to get the csr generated

        > cd /etc/ssl/2021 #or whatever folder you created
        > lcd C:\lynx2021 #location you want to put the file on your local computer
        > get lynx.societyfortheblind.org.csr
        
* When you get the files back for the ssl, use putty psftp to put them on the server
        
        > cd /etc/ssl/2021 #or whatever folder you created
        > lcd C:\lynx2021 #location wher the file is on your local computer
        > put lynx.societyfortheblind.org.csr
        
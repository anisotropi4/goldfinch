### A set of scripts to generate and search 128 ordered sha1sum hash files for passwords known to be hacked  

0) These are shell-scripts that run on a Unix or Linux environment running a POSIX compliant shell with the `p7zip`, GNU `split`, `sha1sum` and `tr` command-line installed

1) Download the 9.78GB `p7zip` compressed `SHA-1 ordered by hash` password file from https://haveibeenpwned.com/Passwords (I recommend using the torrent) 

2) Run the script `create-sha-list.sh`
```$ ./create-sha-list.sh```

* This decompresses the compresses the `SHA-1 ordered by hash` password file
* Splits this text file into 128 smaller files for indexing
* Stores these in the data directory, and
* Creates the `sha-list.txt` index file

3) Run the script `./check-passwd.sh` and type in the passwords to check on the command line:

```$ ./check-passwd.sh
Count the number of times a password is in a list of hacked sha1sum hash keys
type in password:```

If the password the number of times this password has been used is output:
```type in password:
p@ssword
36E618512A68721F032470BB0891ADEF3362CFA9 count 13429
type in password:```

If the password is not found `count not found` is output:
type in password:
```type in password:
thisisapasswordthatdoesntexist
67E2392763100D7C06F767DED5CFFFDB552F759C count not found
type in password:```

Use Ctrl-C to exit

##Acknowledgments

Thanks to Troy Hunt and https://haveibeenpwned.com/  for making this data available

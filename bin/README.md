# goldfinch dependencies

I found the build and installation of the `xml-to-json` utility (a dependency of the `xml-to-ndjson.sh` script) required some fettling. To help with this my install notes are as follows:
  
### **xml-to-json**

The `xml-to-json` utilitiy is a Haskell source code build. On my Debian based Linux test environment I found the following worked:

  * Clone the latest `xml-to-json` source code from github into a suitable build directory:

`$ git clone https://github.com/sinelaw/xml-to-json`

  * Install Haskell `cabal` environment, and `curl` and `expat1` development libraries:

`$ sudo apt install cabal-install libcurl4-gnutls-dev libexpat1-dev`

  * Download Haskell configuration and dependencies:

Run the following command to download Haskell dependencies. By default this appears to create a `.ghc` configuration and `.cabal` installation directory in the user-home directory. 

`$ cabal update`

  * Build and install the `xml-to-json` utility:

Run the build and install command. By default this creates a stand-alone executable `xml-to-json` in the `.cabal/bin` subdirectory, that is `~/.cabal/bin`

`$ cd xml-to-json
$ cabal install xml-to-json`

  * Add the `xml-to-json` to the shell executable path

On my environment I created a symbolic link from the `.cabal/bin` file to `~/bin` as `~/bin` was already in the `$PATH` shell executable path:

`$ cd ~/bin
$ ln -s ~/.cabal/bin/xml-to-json`
 
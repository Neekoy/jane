#!/bin/bash
 
echo
 
PARUSER="parhmihaylov"
 
if [ $# -gt 0 ]; then
        DOMO=$1
else
        echo "Please enter a valid domain name."
fi
 
if [[ "$1" =~ "http://" ]]; then
        DOM=$(echo $DOMO | awk -F"/" '{print $3}');
else
        DOM=${DOMO}
fi
 
if [[ "$1" =~ (zeus|ursa|venus|sirius|titan|wolf|callisto|xena|akira|defiant|quark|chimera) ]]; then
        HOST=$1.servers.eqx.misp.co.uk
        TYPE="Shared cPanel"
        IP=$(dig $HOST +short)
elif [[ "$1" =~ (caprica|bajor|kronos|risa|mercury|europa|saturn|mars|boroth|jupiter|pluto|otion|neptune) ]]; then
        HOST=$1.servers.rbl-mer.misp.co.uk
        TYPE="Shared cPanel"
        IP=$(dig $HOST +short)
elif [[ "$1" =~ (freedom|domtest|excelsior|galaxy) ]]; then
        HOST=$1.servers.prgn.misp.co.uk
        TYPE="Shared cPanel"
        IP=$(dig $HOST +short)
elif [[ "$1" =~ (raven|geneva|flint|trinidad|t11|york|thermalthree|lapland|athens|bogota|exeter|caracas|glasgow|venice|kenya|turin|oregon|morocco|douglas|johnstone|havana|westminster|rome|jamaica|eden|ipswich|nepal|utah|quebec|campbell|seattle|plymouth|balmoral|zurich|isle|newe|hatton|muchalls|knock|airth|leslie|ormond|fyvie|patrick) ]]; then
        HOST=$1.footholds.net
        TYPE="Shared cPanel"
        IP=$(dig $HOST +short)
elif [[ "$1" =~ (theta|iota|kappa|omicron|alpha|zeta|lambda|epsilon|omega|beta|sigma|gamma|delta|tau2) ]]; then
        HOST=$1.srv2.com
        TYPE="Shared cPanel"
        IP=$(dig $HOST +short)
elif [[ "$1" = "ns"?? ]]; then
        HOST=$1.sovdns.com
        IP=$(dig $HOST +short)
else
        if [[ "$2" == "-s" ]]; then
                HOST=$1.servers.prgn.misp.co.uk
                IP=`dig $HOST +short`
        else
                IP=`dig $DOM +short`
                HOST=`host $IP | sed 's/.* \([^ ]\)/\1/' | sed 's/.$//'` &>/dev/null
        fi
fi
 
purple="$(tput setaf 2)"
bold="$(tput bold)"
white="$(tput setaf 8)"
end="$(tput sgr0)"

if [ -z "$IP" ]; then
        echo "The host $bold$purple$DOM$end doesn't seem to have an A record set up. Please investigate." 
        echo
        exit
else
        :
fi
 
VIDA="footholds"
TSO="servers.eqx.misp"
TSO2="servers.rbl-mer.misp"
TSO3="servers.prgn.misp"
ROUTE="srv2.com"
COM="sovdns.com"
 
IPOWN="whois $IP"
 
if [[ "$IP" == "188.65.114.122" ]] || [[ "$IP" == "185.24.99.98" ]] || [[ "$IP" == "95.142.152.194" ]] || [[ "$IP" == "95.142.152.195" ]] || [[ "$IP" == "91.208.99.12" ]]; then
        echo -e "The domain$purple$bold $DOM$end is hosted on our$purple$bold Cloud platform$end ($bold$purple$IP$end)."
#echo
 
#echo Launching $purple$bold Cloud control panel$end login page.
#xdg-open https://control.gridhost.co.uk/admin_panel/loginas.php &>/dev/null
 
echo
        
exit
fi
 
if [[ "$IP" == "188.65.117.99" ]] || [[ "$IP" == "188.65.117.100" ]] || [[ "$IP" == "188.65.117.98" ]]; then
        echo
        echo "The domain ${purple}${bold}${DOM} ${end}is hosted on our SiteBulder Server"
        echo
        exit
fi
 
if [[ "$HOST" =~ "$VIDA" ]]; then
        PORT="3784"
        USER="$PARUSER"
        BRAND="Vidahost"
        TYPE="Shared cPanel"
elif [[ "$HOST" =~ "$TSO" ]] || [[ "$HOST" =~ "$TSO2" ]] || [[ "$HOST" =~ "$TSO3" ]]; then
        if [[ "$HOST" =~ (galaxy|bajor|boroth|caprica|chimera|europa|jupiter|kronos|mars|mercury|quark|risa|saturn|akira|callisto|defiant|neptune|orion|pluto|sirius|titan|ursa|venus|vortex|wolf|xena|zeus|excelsior|freedom) ]]; then
        PORT="2510"
        USER="$PARUSER"
        BRAND="TsoHost"
        TYPE="Shared cPanel"
        else
        PORT="22"
        USER="root"
        BRAND="TsoHost"
        TYPE="Dedicated"
        SHOST=${HOST%%.*}
        echo ${SHOST} | xclip
        fi
elif [[ "$HOST" =~ "$ROUTE" ]]; then
        PORT="2510"
        USER="$PARUSER"
        BRAND="Hostroute"
        TYPE="Shared cPanel"
elif [[ "$HOST" =~ "$COM" ]]; then
        PORT="2995"
        USER="root"
        BRAND="Compila"
        TYPE="Shared cPanel"
elif [[ "$IPOWN" =~ "Adam Smith" ]]; then
        echo -e "The IP $IP has it's owner listed as Adam Smith so it's ours, and probably doesn't have a PTR record, or it's a different type of server. Please check manually." 
        echo
        exit
else
        echo -e "The IP$purple $IP$end doesn't seem to be owned by our company. Please check manually."
        echo
        exit
fi
 
#echo -e "Launching ${bold}${purple}WHM${end} for the host $bold$purple$HOST$end."
 
#xdg-open https://${HOST}:2087 &>/dev/null
 
echo
 
echo -e "You are now connecting to$bold$purple $DOM$end, on server$bold$purple $HOST $end($bold$purple$IP$end),which is a $bold$purple$TYPE$end server, for the brand $bold$purple$BRAND$end."
 
echo
 
#if [[ "${TYPE}" == "Shared cPanel" ]]; then
# 
#        ssh $USER@$HOST -p $PORT <<EOF
# 
#        custUser=$(sudo grep ${DOM} /etc/userdomains)
# 
#        userNew=$(echo ${custUser} | awk 'END {print $NF}')
# 
#        echo ${userNew}
#        echo ${DOM}
# 
#        if [ -z "userNew" ]; then
#                echo
#                print "${purple}The domain name ${bold}${$DOM}${end}${purple} doesn't seem to be located on this server. Please check manually${end}"
#                echo
#                exit
#        fi
# 
#        chDir () {
#                cd /home/${userNew}/
#        }
# 
#        chDir
# 
#        echo
#        echo "${purple}You are now logged in as username ${bold}${userNew}${end}${purple} for the domain ${bold}${DOM}${end}${purple}.${end}"
#        echo
# 
#        sudo su -s /bin/bash ${userNew}
#        EOF
#else
ssh $USER@$HOST -p $PORT
#fi

#!/bin/bash

#COLORS
RED="$(tput setaf 196)"
YELLOW="$(tput setaf 11)"
GREEN="$(tput setaf 47)"
BLUE="$(tput setaf 51)"
ENDC="$(tput sgr0)"

declare -a banner=(
"██╗  ██╗████████╗████████╗███████╗  ███████╗██╗   ██╗███████╗████████╗███████╗███████╗"
"██║  ██║╚══██╔══╝╚══██╔══╝██╔══██║  ██╔══██║██║   ██║██╔════╝╚══██╔══╝██╔════╝██╔══██║"
"███████║   ██║      ██║   ███████║  ██████╦╝██║   ██║███████╗   ██║   █████╗  ██████╔╝"
"██╔══██║   ██║      ██║   ██╔════╝  ██╔══██╗██║   ██║ ╚═══██║   ██║   ██╔══╝  ██╔══██╗"
"██║  ██║   ██║      ██║   ██║       ███████║████████║███████║   ██║   ███████╗██║  ██║"
"╚═╝  ╚═╝   ╚═╝      ╚═╝   ╚═╝       ╚══════╝ ╚══════╝ ╚═════╝   ╚═╝   ╚══════╝╚═╝  ╚═╝"
)


let random=$(shuf -i 1-4 -n 1)

if [[ $random -eq 1 ]]
then
	TOP=$RED
	BASE=$YELLOW
elif [[ $random -eq 2 ]]
then
	TOP=$GREEN
	BASE=$YELLOW
elif [[ $random -eq 3 ]]
then
	TOP=$YELLOW
	BASE=$BLUE
else
	TOP=$BLUE
	BASE=$RED
fi

theme="s/█/$TOP█$ENDC/g;s/╗/$BASE╗$ENDC/g;s/║/$BASE║$ENDC/g;s/╚/$BASE╚$ENDC/g;s/═/$BASE═$ENDC/g;s/╔/$BASE╔$ENDC/g;s/╦/$BASE╦$ENDC/g;s/╝/$BASE╝$ENDC/g;"

for i in "${banner[@]}"; do
    colored=$(echo $i | sed "$theme")
    printf "\n\t$colored"
done

if [ -z "$1" ];
then 
   echo -e "\n${RED}ERROR:ARGUMENT NEEDED [eg: ./run target.com] ${ENDC}"
   exit 1
fi

if dig $1 | grep -q 'NXDOMAIN';
then 
    echo -e "\n${RED}ERROR:DOMAIN NOT FOUND${ENDC}"
    exit 1
fi

echo -e "\n\n[Target: $1] [$(date +"%T") $(date +'%m/%d/%Y')]\n"

start=$(date +%s)

rm -rf output subdomain.list filtered.list #removes files from last session or made by header-check.py
mkdir output
mkdir output/header

rm -rf reports/$1.html #remove to replcae old data
mkdir -p reports #make dir if not exist


touch filtered.list
filter () #Filter funtion
{

	count=$(wc -l < filtered.list)
	total=$(wc -l < subdomain.list)
   	echo -ne "TTL Alive Check\t[$count/$total]"$'\r'
	ttl=$(dig $1 +noall +answer | awk 'END {print $2}') #Last line 2 word
	if [[ ! -z $ttl && $ttl != 0 ]];	#Time to Live Empty or Zero
	then
		echo $1 >> filtered.list
	fi

}
export -f filter

python3 subdomain.py $1
sed -i '/^\./d' subdomain.list #Removes line start with .
sed -i "/[ /*/\/]/d" subdomain.list #Remove line with *, space, /
sed -i "/\.$1$/!d" subdomain.list #Remove line if not end with domain
sort -u -o subdomain.list subdomain.list
echo $1 >> subdomain.list #add original host without subdomain
let filtered=$(wc -l < subdomain.list)
echo -e "\nFiltered: ${BLUE}$filtered${ENDC} Found."
cat subdomain.list | xargs -I{} -P50 bash -c 'filter {}' #Funtion Call

let online=$(wc -l < filtered.list)
let offline=$(($filtered-$online))
echo -ne "Servers: ${GREEN}+$online${ENDC} online ${RED}-$offline${ENDC} Offline\n\n"


#Creating files adn folder to avoid error
touch output/resolved.list output/timeout.list output/unresolved.list

curler () 
{
   YELLOW="$(tput setaf 11)"
   ENDC="$(tput sgr0)"
   original=$(wc -l < filtered.list)
   resolv=$(wc -l < output/resolved.list)
   echo -ne "${YELLOW}[*]${ENDC} Solving headers\t\t[$resolv/$original]"$'\r'
   curl --header "Origin: https://$1" --header "Referer: https://$1" --user-agent "Mozilla" --head -X GET --silent --connect-timeout 30 https://$1 > output/header/https:$1 #Added -X GET to avoid 405 Method Not Allowed
   #Storing error value of last command
   let error=$?
   #For SSL error sites with error curl: (35)
   if [ $error -eq 35 ]||[ $error -eq 60 ]
   then
   	rm -rf output/header/https:$1 #Remove empty file created before
   	curl --header "Origin: https://$1" --header "Referer: https://$1" --user-agent "Mozilla" --head -X GET --silent --connect-timeout 30 $1 > output/header/http:$1
   	error=$?
   fi
   
   if [[ $error != 0 ]];
   then
	rm -rf output/header/https:$1 output/header/http:$1 #Remove empty file created before
	#For unresolved sites with error curl: (6)
   	if [[ $error == 6 ]];
   	then
   		echo $1 >> output/unresolved.list
   	#Timeout curl error curl: (28)
   	elif [[ $error == 28 ]];
   	then
   		echo $1 >> output/timeout.list
   	#For other curl errors
   	else
   		echo $1 >> output/error-$error.list
   	fi
   else
   	echo $1 >> output/resolved.list
   fi
} 
export -f curler
cat filtered.list | xargs -I{} -P50 bash -c 'curler {}'

let resolv=$(wc -l < output/resolved.list)
let timeout=$(wc -l < output/timeout.list)

echo -n "${TOP}[i]${ENDC} Solving headers...done"
echo -e "\t($resolv : Resolved | $timeout : Timeouts)"

python3 report.py output

end=$(date +%s)

mv report.html reports/$1.html
rm -rf output subdomain.list filtered.list

echo -e "\n\n[Saved: reports/$1.html] [Time: $(($end-$start))s]\n"

read -p "Open saved report (y/n): " -n 1 -r
if [[ $REPLY =~ ^[Yy]$ ]]
then
    open reports/$1.html
fi


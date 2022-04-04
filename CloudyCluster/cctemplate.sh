#!/bin/bash
#Usage: ./cctemplate.sh <path where files are downloaded> <text file that contains the download links> 
#Reading the files from download.sh
while IFS= read -r FILE
do
#Printing the name of the file
echo "$FILE"
#Creating a template for a job
cat <<EOF > "download.sh"
#!/bin/bash
#Headers 1 node, 1 cpu, 4 Gigs of ram
#SBATCH -N 1
#CC -cpu 1
#CC -mem 4096
#Printing the file names that are being downloaded
echo "$FILE"
#-p means if not exist create
#Making the directory for the files to download into
#cd goes to the directory
mkdir -p $1 && cd $1
#Downloading the file from the web
wget $FILE 

EOF
 
#submitting the job to cloudy cluster queue
ccqsub download.sh
#Ending loop
done < "$2"
 

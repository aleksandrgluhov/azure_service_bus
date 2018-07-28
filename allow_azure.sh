#!/bin/sh

# constants init
asb_dir="/tmp/asb"
time_stamp=`date +%Y%m%d%H%M%S`
log_file="$asb_dir/asb2ipfw_$time_stamp.log"
table_id=25

# logging init
exec 3>&1 4>&2
trap 'exec 2>&4 1>&3' 0 1 2 3
exec 1>$log_file 2>&1

# commands init
ls_cmd="/bin/ls"
cat_cmd="/bin/cat"
wc_cmd="/usr/bin/wc"
ipfw_cmd="/sbin/ipfw"

# program start
azure_regions="$asb_dir/*.txt"
regions_count=`$ls_cmd $azure_regions | $wc_cmd -l`

if [ "$regions_count" -gt "0" ]; then
	
	# flush Azure Service Bus ip table
	echo "Azure Service Bus regions dir contains $regions_count files. Okay, flushing $table_id ipfw table!"
	$ipfw_cmd table $table_id flush
	
	# fill Azure Service Bus ip table with new addresses
	for region in `$ls_cmd $azure_regions`; do
		
        	ip_count=`$cat_cmd $region | $wc_cmd -l`
        	
		if [ "$ip_count" -gt "0" ]; then
                	
			echo "Region: $region appended to $table_id ipfw table: $ip_count ips"
			for ip in `$cat_cmd $region`; do
				
				# add each ip of region to $table_id ipfw table
				$ipfw_cmd table $table_id add $ip	
			done
        	else
                	echo "$region file is empty."
        	fi
		
		# remove region file.
		# echo "Removing: $region"
		# rm $region
	done
else
	echo "$azure_regions dir is empty."
fi

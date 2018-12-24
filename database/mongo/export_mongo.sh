#!/bin/sh

collections=("ad_act_day" "ad_act_hour" "ad_app_day" "ad_group_day" "ad_group_hour" "ad_hekan_day" "ad_hekan_hour" "ad_id_day" "ad_id_hour" "ad_import_day" "ad_import_hour" "ad_md_day" "ad_md_hour" "ad_plan_day" "ad_plan_hour" "ad_tone_day" "ad_tone_hour" "ad_user_day" "ad_user_hour" "app_area_day" "app_area_hour" "md_app_day" "md_app_hour" "md_appcp_day" "md_appcp_hour" "md_hekan_day" "md_hekan_hour" "md_import_day" "md_import_hour" "md_posid_day" "md_posid_hour" "md_site_day" "md_site_hour" "system.indexes" "wlan_day")
for coll in ${collections[@]}
do
    cmd="mongoexport -h 172.29.160.78 --port 40000 -d sdpp_4mp_exp -c ${coll} -q '{date:{\$gt:1470039971}}' -o /home/work/data/sdpp_4mp_exp_${coll}.dat"
    echo ${cmd}
    eval $cmd
done


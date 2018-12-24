from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import time
import sys
from info import load_ad_info,get_cnzz_id,cnzz_link
import config
from db_api import connect

sys.path.append(".")

#conn =  connect("180.96.26.186",33966,"root","jshb114@nj",db="report")
#cursor=conn.cursor()

def fetch_ad_cnzz_data(cnzz_info):
    dcap = dict(DesiredCapabilities.PHANTOMJS)
    dcap["phantomjs.page.settings.userA"] = (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:25.0) Gecko/20100101 Firefox/25.0 "
    )
    browser=webdriver.PhantomJS(executable_path='./phantomjs',desired_capabilities=dcap)

    #browser.set_window_size(800, 600)
    #url="http://new.cnzz.com/v1/login.php?siteid=1258584969" 

    for k,v in cnzz_info.keys():
        for js in ("show_js","click_js"):
            id = get_cnzz_id(cnzz_info[k][js])
            if not id:
                continue
            url = cnzz_link(id)
            browser.get(url)
            #browser.implicitly_wait(20)
            browser.find_element_by_name("password").send_keys("bc@123456")    
            browser.find_element_by_name("getdata").click()

            #time.sleep(2)
            #print browser.current_url    
            time.sleep(10)
            #browser.implicitly_wait(20)
            curr_data_element = browser.find_element_by_xpath("//table[@id=\"overview_top_order_table\"]/tbody/tr[2]/td[2]")
            #yesterday_total_element = browser.find_element_by_xpath("//table[@id=\"overview_top_order_table\"]/tbody/tr[3]/td[2]")
            #print "curr_data:" + curr_data_element.text
            #print "yesterday total:" + yesterday_total_element.text
            cnzz_info[k]["%s_data" % js] = curr_data_element.text
    
    browser.quit()

def fetch_demand_cnzz_data(demand_info):
    dcap = dict(DesiredCapabilities.PHANTOMJS)
    dcap["phantomjs.page.settings.userAgent"] = (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:25.0) Gecko/20100101 Firefox/25.0 "
    )
    browser=webdriver.PhantomJS(executable_path='./phantomjs',desired_capabilities=dcap)

    #browser.set_window_size(800, 600)
    #url="http://new.cnzz.com/v1/login.php?siteid=1258584969"
    out_dict={}
    for k,v in demand_info.iteritems():
        for _id, passwd in v.items():
            if not _id:
                continue
            url = cnzz_link(_id)
            #print _id,url,passwd

            browser.get(url)
            #browser.implicitly_wait(20)
            browser.find_element_by_name("password").send_keys(passwd)
            browser.find_element_by_name("getdata").click()

            #time.sleep(2)
            #print browser.current_url    

            #browser.implicitly_wait(8)
            time.sleep(10)
            curr_data_element = browser.find_element_by_xpath("//table[@id=\"overview_top_order_table\"]/tbody/tr[2]/td[2]")
            #yesterday_total_element = browser.find_element_by_xpath("//table[@id=\"overview_top_order_table\"]/tbody/tr[3]/td[2]")
            #print "today:" + str(_id) + ":" + curr_data_element.text
            #print "yesterday total:" + yesterday_total_element.text
            #cnzz_info[k]["%s_data" % js] = curr_data_element.text
            #sql= "insert into ads_cnzz (demand_id,cnzz,time) values(k,int(curr_data_element.txt),)"
            out_dict[k]=curr_data_element.text
    
    browser.quit()
    return out_dict
    

#cnzz_info={}
#load_ad_info(cnzz_info)
#fetch_demand_cnzz_data(config.demand_cnzz)

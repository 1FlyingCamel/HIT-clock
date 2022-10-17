import os
import traceback
from time import sleep
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from PIL import Image
import ddddocr

USERNAME= '21B902013'
PASSWORD= 'Aa2303831.'
LOCATION= "黑龙江省哈尔滨市南岗区"
Location=[45.59777,126.63729]

print('初始化浏览器')
ua = 'Mozilla/5.0 (iPhone; CPU iPhone OS 10_0_1 like Mac OS X) AppleWebKit/602.1.50 (KHTML, like Gecko) Mobile/14A403 NetType/WIFI Language/zh_CN'
app = 'HuaWei-AnyOffice/1.0.0/cn.edu.hit.welink'
option = webdriver.ChromeOptions()
option.headless = True
option.add_argument('user-agent='+ua)
s=Service("/usr/bin/chromedriver")
driver = webdriver.Chrome(service=s,options=option)

print('正在上报')

driver.execute_cdp_cmd(
    "Browser.grantPermissions",
    {
        "origin": "https://xg.hit.edu.cn/zhxy-xgzs/xg_mobile/xsMrsbNew/edit",
        "permissions": ["geolocation"]
    },
)
driver.execute_cdp_cmd("Emulation.setGeolocationOverride", {
	"latitude": Location[0],
	"longitude": Location[1],
	"accuracy": 100
})

driver.get('https://ids.hit.edu.cn/authserver/login')
sleep(3)
driver.find_element(By.ID, 'username').send_keys(USERNAME)
sleep(3)
driver.find_element(By.ID,'password').send_keys(PASSWORD)
sleep(3)
driver.find_element(By.ID,'login_submit').click()


def tryClick(id):
	try:
		driver.execute_script(f'document.getElementById("{id}").click()')
	except:
		print(f'No such checkbox: {id}')
		pass


def yzm():
	try:
		# 获取验证码
		# 获取验证码
		operation = True
		counter = 0
		while (operation):
			if counter > 5:
				operation = False
			WebDriverWait(driver, 10).until(
                		EC.presence_of_element_located((By.XPATH, "//*[@id='imgObjjgRegist']")))
			imgelement = driver.find_elements(By.XPATH, '//*[@id="imgObjjgRegist"]')  # 定位验证码
			if not imgelement:
				return
			try:
				imgelement[0].screenshot('./save.png')
			except Exception as e:
				print("截图失败")
				print(e)
				counter += 1
				continue
			# 验证码识别
			ocr = ddddocr.DdddOcr()
			with open('./save.png', 'rb') as f:
				img_bytes = f.read()
				res = ocr.classification(img_bytes)
			f.close()
			print(res)
			driver.find_element(By.ID,'yzm').send_keys(res)
			driver.find_element(By.ID,'pass-dialog').click()

			counter += 1
			sleep(1)
			if not driver.find_elements(By.CLASS_NAME, "weui-toptips_warn"):
				operation = False
	except Exception as e:
		print("验证码处理失败")
		print(e)

success = False
for i in range (0, 1):
	try:
		driver.get('https://xg.hit.edu.cn/zhxy-xgzs/xg_mobile/xsMrsbNew/edit')
		driver.maximize_window()
		driver.set_window_size(800, 1200)
		js = "window.scrollBy(0,500);"
		driver.execute_script(js)
		time.sleep(5)
		driver.find_element(By.XPATH, '/html/body/div[2]/div[2]/div[2]/div/div/div/div[17]/div[2]/div/div/span').click()
		sleep(5)
		tryClick("txfscheckbox1")
		tryClick("txfscheckbox2")
		tryClick("txfscheckbox3")
		sleep(5)
		js = "window.scrollBy(0,1500);"
		driver.execute_script(js)
		a=driver.find_element(By.XPATH,"/html/body/div[2]/div[2]/div[2]/div/div/div[1]/div[66]/div/div/span[1]")
		driver.execute_script("arguments[0].click();",a)
		sleep(5) # 防止有验证码没加载
		yzm()
		success = True
		break
	except:
		traceback.print_exc()
		print('失败' + str(i+1) + '次，正在重试...')
driver.quit()
if success:
	print('上报完成')
else:
	raise Exception('上报多次失败，可能学工系统已更新')


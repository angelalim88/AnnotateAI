from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import tempfile

class ProdigyHandler:
    def __init__(self, url):
        self.url = url
        self.driver = None
        self.setup_driver()
    
    def setup_driver(self):
        chrome_options = Options()
        temp_dir = tempfile.mkdtemp()
        
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument(f"--user-data-dir={temp_dir}")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--disable-features=VizDisplayCompositor")
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--no-first-run")
        chrome_options.add_argument("--disable-default-apps")
        chrome_options.add_argument("--remote-debugging-port=0")
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.implicitly_wait(5)
            self.driver.set_page_load_timeout(30)
            self.driver.get(self.url)
            print("   Prodigy loaded successfully!")
        except Exception as e:
            print(f"   Error opening Chrome: {e}")
            raise
    
    def get_current_text(self):
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            selectors = [
                ".prodigy-content",
                ".prodigy-task",
                "[data-prodigy-task]",
                ".task-text",
                ".annotation-text",
                ".prodigy-task-text"
            ]
            
            for selector in selectors:
                try:
                    text_element = WebDriverWait(self.driver, 2).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    if text_element.text.strip():
                        return text_element.text.strip()
                except:
                    continue
            
            try:
                body_text = self.driver.find_element(By.TAG_NAME, "body").text
                lines = body_text.split('\n')
                for line in lines:
                    line = line.strip()
                    if len(line) > 20 and len(line) < 500:
                        if not any(ui_word in line.lower() for ui_word in ['button', 'click', 'submit', 'label', 'prodigy']):
                            return line
                
                return body_text[:200] if body_text else None
            except:
                return None
            
        except Exception as e:
            print(f"   Error getting text: {e}")
            return None
    
    def click_label(self, label_name):
        try:
            formatted_label = label_name.upper()
            selector = f"//label[@data-prodigy-label='{formatted_label}']"
            
            try:
                label_element = WebDriverWait(self.driver, 3).until(
                    EC.element_to_be_clickable((By.XPATH, selector))
                )
                
                self.driver.execute_script("arguments[0].scrollIntoView(true);", label_element)
                time.sleep(0.2)
                
                label_element.click()
                print(f"   ✅ Selected label: {formatted_label}")
                time.sleep(0.3)
                return True
                
            except Exception as e:
                print(f"   ❌ Label '{formatted_label}' not found: {e}")
                return False
        
        except Exception as e:
            print(f"   ❌ Error clicking label {label_name}: {e}")
            return False

    def annotate_text_spans(self, label_name):
        try:
            text_selectors = [
                ".prodigy-content",
                ".prodigy-task",
                "[data-prodigy-task]",
                ".annotation-text",
                ".prodigy-task-text"
            ]
            
            for selector in text_selectors:
                try:
                    text_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if text_elements:
                        text_element = text_elements[0]
                        
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", text_element)
                        time.sleep(0.2)
                        
                        text_element.click()
                        print(f"   ✅ Annotated text for {label_name}")
                        time.sleep(0.3)
                        return True
                except Exception as e:
                    continue
            
            try:
                clickable_elements = self.driver.find_elements(By.XPATH, "//*[contains(@class, 'clickable') or contains(@onclick, '') or @role='button']")
                for element in clickable_elements:
                    if element.text and len(element.text) > 10:
                        element.click()
                        print(f"   ✅ Annotated clickable text for {label_name}")
                        time.sleep(0.3)
                        return True
            except:
                pass
            
            print(f"   ❌ Could not annotate text for {label_name}")
            return False
            
        except Exception as e:
            print(f"   ❌ Error annotating text: {e}")
            return False

    def process_multiple_labels(self, labels_list):
        success_count = 0
        
        for label_name in labels_list:
            print(f"   🎯 Processing label: {label_name}")
            
            if self.click_label(label_name):
                if self.annotate_text_spans(label_name):
                    success_count += 1
                else:
                    print(f"   ❌ Failed to annotate text for {label_name}")
            else:
                print(f"   ❌ Failed to select label {label_name}")
            
            time.sleep(0.5)
        
        return success_count > 0

    def submit_task(self):
        try:
            selectors = [
                "//button[contains(@class, 'prodigy-button-accept')]",
                "//button[@data-key='accept']",
                "//button[contains(@style, 'background') and contains(@style, 'green')]",
                "//div[contains(@class, 'prodigy-button') and contains(@class, 'accept')]",
                "//button[contains(@class, 'accept')]",
                "//button[contains(@title, 'Accept')]",
                "//button[contains(@aria-label, 'Accept')]",
                "//*[@role='button' and contains(@class, 'accept')]"
            ]
            
            for selector in selectors:
                try:
                    submit_btn = WebDriverWait(self.driver, 2).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", submit_btn)
                    time.sleep(0.2)
                    
                    submit_btn.click()
                    print(f"   ✅ Task submitted successfully")
                    time.sleep(0.5)
                    return True
                except:
                    continue
            
            try:
                submit_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Submit') or contains(text(), 'Accept') or contains(text(), 'Next')]")
                if submit_buttons:
                    submit_buttons[0].click()
                    print(f"   ✅ Task submitted with fallback method")
                    time.sleep(0.5)
                    return True
            except:
                pass
            
            print("   ❌ Submit button not found")
            return False
            
        except Exception as e:
            print(f"   ❌ Error submitting task: {e}")
            return False
    
    def click_ignore(self):
        try:
            selectors = [
                "//button[@data-key='ignore']",
                "//button[contains(text(), 'Ignore')]",
                "//button[contains(text(), 'Skip')]",
                "//button[contains(@class, 'ignore')]",
                "//button[contains(@title, 'Ignore')]"
            ]
            
            for selector in selectors:
                try:
                    ignore_btn = WebDriverWait(self.driver, 2).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    ignore_btn.click()
                    print("   ⏭️ Task ignored/skipped")
                    time.sleep(0.5)
                    return True
                except:
                    continue
            
            print("   ❌ Ignore button not found")
            return False
            
        except Exception as e:
            print(f"   ❌ Error clicking ignore: {e}")
            return False
    
    def auto_save_progress(self):
        try:
            save_selectors = [
                "//button[contains(@class, 'save')]",
                "//button[contains(@title, 'Save')]",
                "//button[contains(@aria-label, 'Save')]",
                "//*[contains(@class, 'save-button')]",
                "//div[contains(@class, 'prodigy-sidebar')]//button",
                "//aside//button[contains(@class, 'button')]",
                "//*[@role='button' and contains(@class, 'save')]",
                "//button[contains(text(), 'Save')]"
            ]
            
            for selector in save_selectors:
                try:
                    save_btn = WebDriverWait(self.driver, 2).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", save_btn)
                    time.sleep(0.2)
                    
                    save_btn.click()
                    print(f"   💾 Progress saved successfully")
                    time.sleep(1)
                    return True
                except:
                    continue
            
            try:
                sidebar_buttons = self.driver.find_elements(By.XPATH, "//aside//button | //div[contains(@class, 'sidebar')]//button")
                for btn in sidebar_buttons:
                    if btn.is_displayed() and btn.is_enabled():
                        btn.click()
                        print(f"   💾 Progress saved with sidebar button")
                        time.sleep(1)
                        return True
            except:
                pass
            
            print("   ❌ Save button not found")
            return False
            
        except Exception as e:
            print(f"   ❌ Error saving progress: {e}")
            return False
    
    def check_no_tasks(self):
        try:
            no_task_texts = [
                "No tasks available",
                "Make sure to save your progress",
                "No more tasks",
                "All tasks completed",
                "Session completed",
                "Annotation complete"
            ]
            
            page_text = self.driver.find_element(By.TAG_NAME, "body").text.lower()
            
            for text in no_task_texts:
                if text.lower() in page_text:
                    return True
            
            try:
                labels = self.driver.find_elements(By.XPATH, "//label[@data-prodigy-label]")
                if not labels:
                    return True
            except:
                pass
            
            return False
            
        except Exception as e:
            print(f"   Error checking task status: {e}")
            return False
    
    def close(self):
        if self.driver:
            try:
                self.driver.quit()
                print("   Browser closed successfully")
            except Exception as e:
                print(f"   Error closing browser: {e}")

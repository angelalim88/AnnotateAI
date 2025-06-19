from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import tempfile
import os

class ProdigyHandler:
    def __init__(self, url):
        self.url = url
        self.driver = None
        self.setup_driver()
    
    def setup_driver(self):
        """Setup Chrome driver dengan unique user data directory"""
        chrome_options = Options()
        
        # Buat temporary directory untuk user data
        temp_dir = tempfile.mkdtemp()
        
        # Chrome options untuk menghindari conflict
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--remote-debugging-port=0")
        chrome_options.add_argument(f"--user-data-dir={temp_dir}")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--disable-features=VizDisplayCompositor")
        
        # Enable headless mode untuk menghindari conflict
        chrome_options.add_argument("--headless")
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.get(self.url)
            print("   Prodigy loaded successfully!")
        except Exception as e:
            print(f"   Error opening Chrome: {e}")
            raise

    
    def get_current_text(self):
        """Ambil teks dari task yang sedang aktif"""
        try:
            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Coba berbagai selector untuk text content
            selectors = [
                ".prodigy-content",
                ".prodigy-task",
                "[data-prodigy-task]",
                ".task-text",
                ".annotation-text"
            ]
            
            for selector in selectors:
                try:
                    text_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if text_element.text.strip():
                        return text_element.text.strip()
                except:
                    continue
            
            # Fallback: ambil semua text dari body
            body_text = self.driver.find_element(By.TAG_NAME, "body").text
            print(f"   Fallback: using body text (first 200 chars): {body_text[:200]}...")
            return body_text
            
        except Exception as e:
            print(f"   Error getting text: {e}")
            return None
    
    def click_label(self, label_name):
        """Click label tertentu di Prodigy"""
        try:
            # Coba berbagai selector untuk button label
            selectors = [
                f"//button[contains(text(), '{label_name}')]",
                f"//span[contains(text(), '{label_name}')]",
                f"//div[contains(@class, 'label') and contains(text(), '{label_name}')]",
                f"//*[contains(@data-label, '{label_name}')]"
            ]
            
            for selector in selectors:
                try:
                    label_btn = self.driver.find_element(By.XPATH, selector)
                    label_btn.click()
                    return True
                except:
                    continue
            
            print(f"   Label '{label_name}' not found")
            return False
            
        except Exception as e:
            print(f"   Error clicking label {label_name}: {e}")
            return False
    
    def click_multiple_labels(self, labels):
        """Click multiple labels untuk satu task"""
        success_count = 0
        for label in labels:
            if self.click_label(label):
                success_count += 1
                time.sleep(0.5)  # Small delay between clicks
        
        return success_count > 0
    
    def submit_task(self):
        """Submit current task"""
        try:
            # Coba berbagai selector untuk submit button
            selectors = [
                "//button[contains(text(), 'Submit')]",
                "//button[contains(text(), 'Accept')]", 
                "//button[contains(@class, 'submit')]",
                "[data-key='accept']",
                ".prodigy-button-accept"
            ]
            
            for selector in selectors:
                try:
                    if selector.startswith("//"):
                        submit_btn = self.driver.find_element(By.XPATH, selector)
                    else:
                        submit_btn = self.driver.find_element(By.CSS_SELECTOR, selector)
                    submit_btn.click()
                    return True
                except:
                    continue
            
            print("   Submit button not found")
            return False
            
        except Exception as e:
            print(f"   Error submitting task: {e}")
            return False
    
    def click_ignore(self):
        """Click tombol ignore untuk skip task"""
        try:
            selectors = [
                "[data-key='ignore']",
                "//button[contains(text(), 'Ignore')]",
                "//button[contains(text(), 'Skip')]"
            ]
            
            for selector in selectors:
                try:
                    if selector.startswith("//"):
                        ignore_btn = self.driver.find_element(By.XPATH, selector)
                    else:
                        ignore_btn = self.driver.find_element(By.CSS_SELECTOR, selector)
                    ignore_btn.click()
                    return True
                except:
                    continue
            
            return False
            
        except Exception as e:
            print(f"   Error clicking ignore: {e}")
            return False
    
    def check_no_tasks(self):
        """Check apakah sudah tidak ada task lagi"""
        try:
            no_task_texts = [
                "No tasks available",
                "Make sure to save your progress",
                "No more tasks",
                "All tasks completed"
            ]
            
            page_text = self.driver.find_element(By.TAG_NAME, "body").text
            
            for text in no_task_texts:
                if text.lower() in page_text.lower():
                    return True
            
            return False
            
        except:
            return False
    
    def close(self):
        """Tutup browser"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass

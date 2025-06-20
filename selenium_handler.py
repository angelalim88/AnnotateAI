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
        """Setup Chrome driver dengan better stability"""
        chrome_options = Options()
        
        # Buat temporary directory untuk user data
        temp_dir = tempfile.mkdtemp()
        
        # Chrome options untuk menghindari conflict dan stability
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument(f"--user-data-dir={temp_dir}")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--disable-features=VizDisplayCompositor")
        chrome_options.add_argument("--headless")  # More stable for server
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--no-first-run")
        chrome_options.add_argument("--disable-default-apps")
        chrome_options.add_argument("--remote-debugging-port=0")
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.implicitly_wait(10)  # Global wait
            self.driver.set_page_load_timeout(30)
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
                ".annotation-text",
                ".prodigy-task-text"
            ]
            
            for selector in selectors:
                try:
                    text_element = WebDriverWait(self.driver, 3).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    if text_element.text.strip():
                        return text_element.text.strip()
                except:
                    continue
            
            # Fallback: ambil text dari body tapi filter yang relevan
            try:
                body_text = self.driver.find_element(By.TAG_NAME, "body").text
                # Filter text yang terlalu panjang atau mengandung UI elements
                lines = body_text.split('\n')
                for line in lines:
                    line = line.strip()
                    if len(line) > 20 and len(line) < 500:  # Reasonable text length
                        if not any(ui_word in line.lower() for ui_word in ['button', 'click', 'submit', 'label', 'prodigy']):
                            return line
                
                return body_text[:200] if body_text else None
            except:
                return None
            
        except Exception as e:
            print(f"   Error getting text: {e}")
            return None
    
    def click_label(self, label_name):
        """Click label tertentu di Prodigy berdasarkan HTML structure"""
        try:
            formatted_label = label_name.upper()
            
            # Berdasarkan HTML: click pada label element dengan data-prodigy-label
            selector = f"//label[@data-prodigy-label='{formatted_label}']"
            
            try:
                label_element = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, selector))
                )
                
                # Scroll to element if needed
                self.driver.execute_script("arguments[0].scrollIntoView(true);", label_element)
                time.sleep(0.5)
                
                # Click the label
                label_element.click()
                print(f"   ✅ Selected label: {formatted_label}")
                time.sleep(1)  # Wait for label to be selected
                return True
                
            except Exception as e:
                print(f"   ❌ Label '{formatted_label}' not found: {e}")
                return False
        
        except Exception as e:
            print(f"   ❌ Error clicking label {label_name}: {e}")
            return False

    def annotate_text_spans(self, label_name, query_text):
        """Annotate text spans untuk label yang dipilih"""
        try:
            # Setelah pilih label, cari text yang bisa di-annotate
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
                        # Click pada text element untuk annotate
                        text_element = text_elements[0]
                        
                        # Scroll to element
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", text_element)
                        time.sleep(0.5)
                        
                        # Click to annotate
                        text_element.click()
                        print(f"   ✅ Annotated text for {label_name}")
                        time.sleep(1)
                        return True
                except Exception as e:
                    continue
            
            # Alternative: try to find and click any clickable text
            try:
                clickable_elements = self.driver.find_elements(By.XPATH, "//*[contains(@class, 'clickable') or contains(@onclick, '') or @role='button']")
                for element in clickable_elements:
                    if element.text and len(element.text) > 10:
                        element.click()
                        print(f"   ✅ Annotated clickable text for {label_name}")
                        time.sleep(1)
                        return True
            except:
                pass
            
            print(f"   ❌ Could not annotate text for {label_name}")
            return False
            
        except Exception as e:
            print(f"   ❌ Error annotating text: {e}")
            return False

    def process_multiple_labels(self, labels_and_text):
        """Process multiple labels dengan annotation step-by-step"""
        success_count = 0
        
        for label_name in labels_and_text:
            print(f"   🎯 Processing label: {label_name}")
            
            # Step 1: Click label
            if self.click_label(label_name):
                # Step 2: Annotate text spans
                if self.annotate_text_spans(label_name, ""):
                    success_count += 1
                else:
                    print(f"   ❌ Failed to annotate text for {label_name}")
            else:
                print(f"   ❌ Failed to select label {label_name}")
            
            time.sleep(1.5)  # Delay between labels
        
        return success_count > 0

    def submit_task(self):
        """Submit current task dengan click tombol centang hijau"""
        try:
            # Coba berbagai selector untuk submit button (tombol centang hijau)
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
                    submit_btn = WebDriverWait(self.driver, 3).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    
                    # Scroll to button
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", submit_btn)
                    time.sleep(0.5)
                    
                    submit_btn.click()
                    print(f"   ✅ Task submitted successfully")
                    time.sleep(2)  # Wait for next task to load
                    return True
                except:
                    continue
            
            # Fallback: try to find any submit-like button
            try:
                submit_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Submit') or contains(text(), 'Accept') or contains(text(), 'Next')]")
                if submit_buttons:
                    submit_buttons[0].click()
                    print(f"   ✅ Task submitted with fallback method")
                    time.sleep(2)
                    return True
            except:
                pass
            
            print("   ❌ Submit button not found")
            return False
            
        except Exception as e:
            print(f"   ❌ Error submitting task: {e}")
            return False
    
    def click_ignore(self):
        """Click tombol ignore untuk skip task"""
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
                    ignore_btn = WebDriverWait(self.driver, 3).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    ignore_btn.click()
                    print("   ⏭️ Task ignored/skipped")
                    time.sleep(2)
                    return True
                except:
                    continue
            
            print("   ❌ Ignore button not found")
            return False
            
        except Exception as e:
            print(f"   ❌ Error clicking ignore: {e}")
            return False
    
    def check_no_tasks(self):
        """Check apakah sudah tidak ada task lagi"""
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
            
            # Check if there are no more clickable elements (indicating no more tasks)
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
    
    def get_page_info(self):
        """Get current page info for debugging"""
        try:
            current_url = self.driver.current_url
            page_title = self.driver.title
            page_text = self.driver.find_element(By.TAG_NAME, "body").text[:200]
            
            print(f"   Debug - URL: {current_url}")
            print(f"   Debug - Title: {page_title}")
            print(f"   Debug - Page text: {page_text}...")
            
        except Exception as e:
            print(f"   Error getting page info: {e}")
    
    def close(self):
        """Tutup browser dan cleanup"""
        if self.driver:
            try:
                self.driver.quit()
                print("   Browser closed successfully")
            except Exception as e:
                print(f"   Error closing browser: {e}")

import time
from config import PRODIGY_URL, DELAY_BETWEEN_TASKS, AUTO_SAVE_INTERVAL
from data_processor import load_all_datasets, extract_non_neutral_labels
from rag_handler import RAGHandler
from selenium_handler import ProdigyHandler

def process_single_task(prodigy, rag):
    try:
        current_text = prodigy.get_current_text()
        if not current_text:
            print("❌ Tidak bisa ambil text dari task")
            return False
        
        print(f"📝 Text: {current_text[:100]}...")
        
        labels_to_annotate = rag.find_labels_to_annotate(current_text)
        
        if not labels_to_annotate:
            print("⏭️ Tidak ada label yang cocok, skip task")
            return prodigy.click_ignore()
        
        print(f"🎯 Predicted labels: {labels_to_annotate}")
        
        if prodigy.process_multiple_labels(labels_to_annotate):
            print(f"✅ Berhasil process {len(labels_to_annotate)} labels")
            time.sleep(0.5)
            return prodigy.submit_task()
        else:
            print("❌ Gagal process labels")
            return False
        
    except Exception as e:
        print(f"❌ Error in process task: {e}")
        return False

def run_full_automation(prodigy, rag):
    task_count = 0
    success_count = 0
    max_consecutive_errors = 3
    consecutive_errors = 0
    last_save_count = 0
    
    print("\n🚀 Memulai full automation...")
    print(f"💾 Auto-save akan dilakukan setiap {AUTO_SAVE_INTERVAL} task yang berhasil")
    
    while task_count < 1080:
        try:
            if prodigy.check_no_tasks():
                print("\n✅ Semua task selesai!")
                break
            
            print(f"\n📋 Processing task #{task_count + 1}")
            
            if process_single_task(prodigy, rag):
                success_count += 1
                consecutive_errors = 0
                print(f"✅ Task #{task_count + 1} berhasil")
                
                if success_count - last_save_count >= AUTO_SAVE_INTERVAL:
                    print(f"\n💾 Auto-saving progress after {success_count} successful tasks...")
                    if prodigy.auto_save_progress():
                        last_save_count = success_count
                        print(f"✅ Progress saved! Total completed: {success_count}")
                    else:
                        print("❌ Auto-save failed, but continuing...")
                
            else:
                consecutive_errors += 1
                print(f"❌ Task #{task_count + 1} gagal")
                
                if consecutive_errors >= max_consecutive_errors:
                    print(f"❌ Terlalu banyak error berturut-turut. Stopping automation.")
                    break
            
            task_count += 1
            
            if task_count % 25 == 0:
                success_rate = (success_count / task_count) * 100
                print(f"\n📊 Progress Report:")
                print(f"   Tasks processed: {task_count}/1080")
                print(f"   Successful: {success_count}")
                print(f"   Success rate: {success_rate:.1f}%")
                print(f"   Last saved at: {last_save_count} tasks")
            
            time.sleep(DELAY_BETWEEN_TASKS)
            
        except KeyboardInterrupt:
            print("\n⏹️ Automation dihentikan oleh user")
            print("💾 Saving progress before exit...")
            prodigy.auto_save_progress()
            break
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            consecutive_errors += 1
            if consecutive_errors >= max_consecutive_errors:
                break
    
    print(f"\n💾 Final save...")
    if prodigy.auto_save_progress():
        print("✅ Final progress saved!")
    
    success_rate = (success_count / task_count) * 100 if task_count > 0 else 0
    print(f"\n📈 Final Stats:")
    print(f"   Total tasks processed: {task_count}")
    print(f"   Successful: {success_count}")
    print(f"   Success rate: {success_rate:.1f}%")
    print(f"   Total saves performed: {(success_count // AUTO_SAVE_INTERVAL) + 1}")

def test_single_task(prodigy, rag):
    print("\n🧪 Testing single task...")
    
    try:
        current_text = prodigy.get_current_text()
        if not current_text:
            print("❌ Tidak bisa ambil text dari Prodigy")
            return False
        
        print(f"📝 Text yang akan diproses:")
        print(f"   {current_text}")
        
        labels_to_annotate = rag.find_labels_to_annotate(current_text)
        
        print(f"\n🎯 AI memprediksi labels:")
        if labels_to_annotate:
            for i, label in enumerate(labels_to_annotate, 1):
                print(f"   {i}. {label}")
        else:
            print("   Tidak ada label yang cocok (akan di-skip)")
        
        print(f"\n❓ Apakah prediksi AI sudah benar?")
        response = input("   (y)es / (n)o / (s)kip test: ")
        
        if response.lower() == 's':
            return True
        elif response.lower() == 'y':
            print("✅ Test validation passed!")
            return True
        else:
            print("❌ Prediksi belum akurat, coba adjust threshold atau data")
            return False
        
    except Exception as e:
        print(f"❌ Error in test: {e}")
        return False

def test_save_function(prodigy):
    print("\n🧪 Testing save function...")
    
    if prodigy.auto_save_progress():
        print("✅ Save function working!")
        return True
    else:
        print("❌ Save function not working, check selector")
        return False

def main():
    print("🚀 Starting Prodigy Multi-Label Automation...")
    print("=" * 50)
    
    try:
        print("\n📊 Step 1: Loading datasets...")
        df = load_all_datasets()
        print(f"   Loaded {len(df)} total rows from datasets")
        
        print("\n🔍 Step 2: Extracting non-neutral labels...")
        knowledge_data = extract_non_neutral_labels(df)
        print(f"   Extracted {len(knowledge_data)} knowledge entries")
        
        if len(knowledge_data) == 0:
            print("❌ Tidak ada data non-neutral ditemukan!")
            return
        
        print(f"\n📋 Sample knowledge entries:")
        for i, item in enumerate(knowledge_data[:3], 1):
            print(f"   {i}. {item['text'][:50]}... -> {item['prodigy_label']}")
        
        print("\n🧠 Step 3: Setting up RAG system...")
        rag = RAGHandler()
        rag.setup_vectorstore(knowledge_data)
        print("   RAG system ready!")
        
        print(f"\n🌐 Step 4: Opening Prodigy...")
        print(f"   URL: {PRODIGY_URL}")
        prodigy = ProdigyHandler(PRODIGY_URL)
        
        time.sleep(3)
        print("   Prodigy loaded!")
        
        if not test_save_function(prodigy):
            print("⚠️ Save function might not work, but continuing...")
        
        if test_single_task(prodigy, rag):
            print("\n✅ Test berhasil!")
            
            print("\n🤖 Mau lanjut ke full automation?")
            response = input("   (y)es / (n)o: ")
            
            if response.lower() == 'y':
                run_full_automation(prodigy, rag)
            else:
                print("⏹️ Automation dihentikan oleh user")
        else:
            print("\n❌ Test gagal! Periksa konfigurasi dan coba lagi")
    
    except KeyboardInterrupt:
        print("\n\n⏹️ Automation dihentikan oleh user (Ctrl+C)")
    
    except Exception as e:
        print(f"\n❌ Error dalam main function: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        print("\n🧹 Cleaning up...")
        try:
            if 'prodigy' in locals():
                prodigy.close()
            print("   Browser closed")
        except:
            pass
        
        print("\n🏁 Automation selesai!")
        print("=" * 50)

if __name__ == "__main__":
    main()

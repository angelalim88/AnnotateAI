import time
from config import PRODIGY_URL, DELAY_BETWEEN_TASKS
from data_processor import load_all_datasets, extract_non_neutral_labels
from rag_handler import RAGHandler
from selenium_handler import ProdigyHandler

def process_single_task(prodigy, rag):
    """Process 1 task dengan multiple labels"""
    try:
        current_text = prodigy.get_current_text()
        if not current_text:
            print("❌ Tidak bisa ambil text dari task")
            return False
        
        print(f"📝 Text: {current_text[:100]}...")
        
        # Cari label apa saja yang perlu di-annotate
        labels_to_annotate = rag.find_labels_to_annotate(current_text)
        
        print(f"🎯 Predicted labels: {labels_to_annotate}")
        
        if labels_to_annotate:
            # Click semua label yang diprediksi
            success = prodigy.click_multiple_labels(labels_to_annotate)
            if success:
                print(f"✅ Berhasil click {len(labels_to_annotate)} labels")
                # Submit task setelah semua label di-click
                time.sleep(1)  # Wait sebentar sebelum submit
                prodigy.submit_task()
            else:
                print("❌ Gagal click labels")
                return False
        else:
            # Tidak ada label yang cocok, skip task
            print("⏭️ Tidak ada label yang cocok, skip task")
            prodigy.click_ignore()
        
        return True
        
    except Exception as e:
        print(f"❌ Error in process task: {e}")
        return False

def run_full_automation(prodigy, rag):
    """Run full automation untuk semua tasks"""
    task_count = 0
    success_count = 0
    
    print("\n🚀 Memulai full automation...")
    
    while True:
        # Check apakah sudah tidak ada task lagi
        if prodigy.check_no_tasks():
            print("\n✅ Semua task selesai!")
            break
        
        print(f"\n📋 Processing task #{task_count + 1}")
        
        # Process current task
        if process_single_task(prodigy, rag):
            success_count += 1
            print(f"✅ Task #{task_count + 1} berhasil")
        else:
            print(f"❌ Task #{task_count + 1} gagal")
            
            # Tanya user mau lanjut atau stop
            response = input("Ada error. Lanjut? (y/n): ")
            if response.lower() != 'y':
                break
        
        task_count += 1
        
        # Progress info setiap 10 tasks
        if task_count % 10 == 0:
            success_rate = (success_count / task_count) * 100
            print(f"\n📊 Progress: {task_count} tasks, {success_rate:.1f}% success rate")
        
        # Delay before next task
        time.sleep(DELAY_BETWEEN_TASKS)
    
    # Final statistics
    success_rate = (success_count / task_count) * 100 if task_count > 0 else 0
    print(f"\n📈 Final Stats:")
    print(f"   Total tasks: {task_count}")
    print(f"   Successful: {success_count}")
    print(f"   Success rate: {success_rate:.1f}%")

def test_single_task(prodigy, rag):
    """Test process 1 task saja untuk validasi"""
    print("\n🧪 Testing single task...")
    
    try:
        current_text = prodigy.get_current_text()
        if not current_text:
            print("❌ Tidak bisa ambil text dari Prodigy")
            return False
        
        print(f"📝 Text yang akan diproses:")
        print(f"   {current_text}")
        
        # Cari label yang cocok
        labels_to_annotate = rag.find_labels_to_annotate(current_text)
        
        print(f"\n🎯 AI memprediksi labels:")
        if labels_to_annotate:
            for i, label in enumerate(labels_to_annotate, 1):
                print(f"   {i}. {label}")
        else:
            print("   Tidak ada label yang cocok (akan di-skip)")
        
        # Tanya user apakah prediksi benar
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

def main():
    """Main function untuk menjalankan automation"""
    print("🚀 Starting Prodigy Multi-Label Automation...")
    print("=" * 50)
    
    try:
        # 1. Load datasets
        print("\n📊 Step 1: Loading datasets...")
        df = load_all_datasets()
        print(f"   Loaded {len(df)} total rows from datasets")
        
        # 2. Extract knowledge data
        print("\n🔍 Step 2: Extracting non-neutral labels...")
        knowledge_data = extract_non_neutral_labels(df)
        print(f"   Extracted {len(knowledge_data)} knowledge entries")
        
        if len(knowledge_data) == 0:
            print("❌ Tidak ada data non-neutral ditemukan!")
            return
        
        # Show sample knowledge data
        print(f"\n📋 Sample knowledge entries:")
        for i, item in enumerate(knowledge_data[:3], 1):
            print(f"   {i}. {item['text'][:50]}... -> {item['prodigy_label']}")
        
        # 3. Setup RAG
        print("\n🧠 Step 3: Setting up RAG system...")
        rag = RAGHandler()
        rag.setup_vectorstore(knowledge_data)
        print("   RAG system ready!")
        
        # 4. Setup Selenium
        print(f"\n🌐 Step 4: Opening Prodigy...")
        print(f"   URL: {PRODIGY_URL}")
        prodigy = ProdigyHandler(PRODIGY_URL)
        
        # Wait for page to load
        time.sleep(3)
        print("   Prodigy loaded!")
        
        # 5. Test single task
        if test_single_task(prodigy, rag):
            print("\n✅ Test berhasil!")
            
            # Ask user untuk lanjut full automation
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
        # 6. Cleanup
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

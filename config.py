PRODIGY_URL = "https://anotasi.uajy.ac.id/nlp2/?session=220711789"
DATASET_PATHS = [
    "test_preprocess.csv",
    "train_preprocess.csv"
]

LABEL_MAPPING = {
    'fuel_positive': 'fuel_positive',
    'fuel_negative': 'fuel_negative', 
    'machine_positive': 'machine_positive',
    'machine_negative': 'machine_negative',
    'others_positive': 'others_positive',
    'others_negative': 'others_negative',
    'part_positive': 'part_positive',
    'part_negative': 'part_negative',
    'price_positive': 'price_positive',
    'price_negative': 'price_negative',
    'service_positive': 'service_positive',
    'service_negative': 'service_negative'
}

DELAY_BETWEEN_TASKS = 1
SIMILARITY_THRESHOLD = 0.15
AUTO_SAVE_INTERVAL = 1

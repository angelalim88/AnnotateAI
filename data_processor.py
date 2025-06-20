import pandas as pd
from config import DATASET_PATHS

def load_all_datasets():
    all_data = []
    
    for path in DATASET_PATHS:
        df = pd.read_csv(path)
        all_data.append(df)
    
    combined_df = pd.concat(all_data, ignore_index=True)
    return combined_df

def extract_non_neutral_labels(df):
    knowledge_data = []
    
    label_columns = ['fuel', 'machine', 'others', 'part', 'price', 'service']
    
    for _, row in df.iterrows():
        sentence = row['sentence']
        
        for col in label_columns:
            label_value = row[col]
            
            if label_value != 'neutral':
                knowledge_data.append({
                    'text': sentence,
                    'aspect': col,
                    'sentiment': label_value,
                    'prodigy_label': f"{col}_{label_value}"
                })
    
    return knowledge_data

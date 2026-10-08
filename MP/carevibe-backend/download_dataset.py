import os
import json
import urllib.request

DATASET_DIR = os.path.join(os.path.dirname(__file__), 'dataset')
os.makedirs(DATASET_DIR, exist_ok=True)

LABELS = ['sadness', 'joy', 'love', 'anger', 'fear', 'surprise']
SPLITS = {
    'train.txt': 'train',
    'val.txt': 'validation',
    'test.txt': 'test'
}

BASE_URL = "https://datasets-server.huggingface.co/parquet?dataset=dair-ai/emotion"

def fetch_parquet_urls():
    req = urllib.request.Request(BASE_URL, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        return data.get('parquet_files', [])

if __name__ == '__main__':
    try:
        files = fetch_parquet_urls()
        print("Found parquet files:", files)
        import pandas as pd
        for file_info in files:
            split = file_info.get('split')
            url = file_info.get('url')
            config = file_info.get('config')
            if config == 'split' and split in ['train', 'validation', 'test']:
                out_name = 'val.txt' if split == 'validation' else f"{split}.txt"
                out_path = os.path.join(DATASET_DIR, out_name)
                print(f"Downloading {split} from {url}...")
                df = pd.read_parquet(url)
                # df has columns 'text' and 'label' (int)
                df['label_name'] = df['label'].apply(lambda i: LABELS[i] if isinstance(i, int) and 0 <= i < len(LABELS) else i)
                lines = [f"{row['text']};{row['label_name']}" for _, row in df.iterrows()]
                with open(out_path, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(lines))
                print(f"Saved {len(lines)} rows to {out_path}")
    except Exception as e:
        print(f"Error downloading dataset: {e}")

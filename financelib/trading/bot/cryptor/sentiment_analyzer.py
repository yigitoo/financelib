import torch
from torch.utils.data import Dataset, DataLoader
from transformers import BertTokenizer, BertForSequenceClassification, AdamW
import logging
from collections import defaultdict
import numpy as np
from datetime import datetime

from settings import FINE_TUNED_MODEL_PATH
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class SentimentDataset(Dataset):
    def __init__(self, texts, labels, tokenizer, max_length=128):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        text = self.texts[idx]
        label = self.labels[idx]
        encoding = self.tokenizer(text, return_tensors='pt', truncation=True, padding='max_length', max_length=self.max_length)
        return {
            'input_ids': encoding['input_ids'].squeeze(),
            'attention_mask': encoding['attention_mask'].squeeze(),
            'labels': torch.tensor(label, dtype=torch.long)
        }

class SentimentAnalyzer:
    def __init__(self, fine_tuned_path=FINE_TUNED_MODEL_PATH):
        self.tokenizer = BertTokenizer.from_pretrained('ProsusAI/finbert')
        # Fine-tuned model varsa yükle, yoksa orijinal FinBERT’i kullan
        if os.path.exists(fine_tuned_path):
            logging.info(f"Fine-tuned FinBERT modeli yükleniyor: {fine_tuned_path}")
            self.model = BertForSequenceClassification.from_pretrained(fine_tuned_path)
        else:
            logging.info("Fine-tuned model bulunamadı, orijinal FinBERT yükleniyor.")
            self.model = BertForSequenceClassification.from_pretrained('ProsusAI/finbert')

        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model.to(self.device)
        self.model.eval()

        # Coin bazlı sentiment skorları ve ağırlıklar
        self.sentiment_scores = defaultdict(lambda: {'score': 0.0, 'count': 0, 'last_updated': None})
        self.tweet_weight = 0.6
        self.news_weight = 0.4
        self.label_map = {0: 1.0, 1: -1.0, 2: 0.0}  # Pozitif: 0, Negatif: 1, Nötr: 2

    def analyze_text(self, texts, coin_name):
        """Metin listesi için FinBERT ile sentiment analizi"""
        sentiments = []
        for text in texts:
            inputs = self.tokenizer(text, return_tensors='pt', truncation=True, padding=True, max_length=128)
            inputs = {key: val.to(self.device) for key, val in inputs.items()}

            with torch.no_grad():
                outputs = self.model(**inputs)
                logits = outputs.logits
                prediction = torch.softmax(logits, dim=1).cpu().numpy()[0]
                label_idx = np.argmax(prediction)
                sentiment_score = self.label_map[label_idx] * prediction[label_idx]
                sentiments.append(sentiment_score)

        return sentiments

    def fine_tune(self, texts, labels, epochs=3, batch_size=16, learning_rate=2e-5):
        """FinBERT modelini fine-tuning yap"""
        logging.info("FinBERT fine-tuning başlatılıyor...")

        # Veri setini hazırla
        dataset = SentimentDataset(texts, labels, self.tokenizer)
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

        # Optimizer
        optimizer = AdamW(self.model.parameters(), lr=learning_rate)

        # Eğitim döngüsü
        self.model.train()
        for epoch in range(epochs):
            total_loss = 0
            for batch in dataloader:
                optimizer.zero_grad()
                inputs = {key: val.to(self.device) for key, val in batch.items() if key != 'labels'}
                labels = batch['labels'].to(self.device)

                outputs = self.model(**inputs, labels=labels)
                loss = outputs.loss
                loss.backward()
                optimizer.step()

                total_loss += loss.item()

            avg_loss = total_loss / len(dataloader)
            logging.info(f"Epoch {epoch+1}/{epochs}, Ortalama Kayıp: {avg_loss:.4f}")

        # Modeli kaydet
        self.model.save_pretrained(FINE_TUNED_MODEL_PATH)
        self.tokenizer.save_pretrained(FINE_TUNED_MODEL_PATH)
        logging.info(f"Fine-tuned FinBERT modeli kaydedildi: {FINE_TUNED_MODEL_PATH}")

    def update_sentiment_score(self, coin_name, tweet_texts, news_texts):
        """Coin bazlı sentiment skorunu güncelle"""
        tweet_sentiments = self.analyze_text(tweet_texts, coin_name) if tweet_texts else []
        news_sentiments = self.analyze_text(news_texts, coin_name) if news_texts else []

        tweet_avg = np.mean(tweet_sentiments) if tweet_sentiments else 0
        news_avg = np.mean(news_sentiments) if news_sentiments else 0
        combined_score = (self.tweet_weight * tweet_avg + self.news_weight * news_avg)

        current = self.sentiment_scores[coin_name]
        alpha = 0.3
        updated_score = (1 - alpha) * current['score'] + alpha * combined_score if current['count'] > 0 else combined_score

        self.sentiment_scores[coin_name] = {
            'score': updated_score,
            'count': current['count'] + len(tweet_texts) + len(news_texts),
            'last_updated': datetime.now().isoformat()
        }

        logging.info(f"{coin_name} için FinBERT sentiment güncellendi: Skor: {updated_score:.2f}, "
                     f"Tweet Ortalama: {tweet_avg:.2f}, Haber Ortalama: {news_avg:.2f}, "
                     f"Toplam Veri: {self.sentiment_scores[coin_name]['count']}")

        return updated_score

    def get_sentiment_score(self, coin_name, tweet_texts, news_texts):
        if not tweet_texts and not news_texts:
            return self.sentiment_scores[coin_name]['score']
        return self.update_sentiment_score(coin_name, tweet_texts, news_texts)

# Örnek fine-tuning kullanımı
if __name__ == '__main__':
    analyzer = SentimentAnalyzer()
    # Örnek veri seti (gerçek kullanımda kendi veri setinizi sağlamalısınız)
    texts = ["Bitcoin is soaring!", "BTC might drop soon", "Bitcoin hits record high", "Crypto market faces uncertainty"]
    labels = [0, 1, 0, 1]  # Pozitif: 0, Negatif: 1, Nötr: 2
    analyzer.fine_tune(texts, labels, epochs=3, batch_size=2)

    # Fine-tuned model ile sentiment analizi
    tweets = ["Bitcoin is amazing!", "BTC is crashing"]
    news = ["Bitcoin surges", "Market downturn"]
    score = analyzer.get_sentiment_score("bitcoin", tweets, news)
    print(f"Bitcoin Sentiment Score: {score}")

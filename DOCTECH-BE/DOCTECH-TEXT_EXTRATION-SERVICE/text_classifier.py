from transformers import BertTokenizer, BertForTokenClassification, pipeline
import torch

class TextClassifier:
    def __init__(self, model_path="dbmdz/bert-large-cased-finetuned-conll03-english"):
        # Load pre-trained model and tokenizer for NER
        self.tokenizer = BertTokenizer.from_pretrained(model_path)
        self.model = BertForTokenClassification.from_pretrained(model_path)
        self.nlp = pipeline("ner", model=self.model, tokenizer=self.tokenizer)

    def predict(self, text: str) -> dict:
        # Perform NER on the input text
        ner_results = self.nlp(text)

        # Initialize dictionary to store the extracted entities
        entities = {
            "header_name": None,
            "temperature": None,
            "quantity": None,
            "booking": None,
            "carrier": None,
            "feeder": None,
            "vessel": None,
            "port": None,
            "etd": None,
            "eta": None,
            "cy_date": None,
            "return_date": None,
            "destination": None,
        }

        # Post-process the NER results to extract relevant information
        for entity in ner_results:
            entity_text = entity["word"]
            entity_label = entity["entity"]

            # Here, you'd add logic to map recognized entities to your fields
            if "TEMP" in entity_label.upper():
                entities["temperature"] = entity_text
            elif "QUANTITY" in entity_label.upper():
                entities["quantity"] = entity_text
            elif "BOOKING" in entity_label.upper():
                entities["booking"] = entity_text
            elif "CARRIER" in entity_label.upper():
                entities["carrier"] = entity_text
            elif "FEEDER" in entity_label.upper():
                entities["feeder"] = entity_text
            elif "VESSEL" in entity_label.upper():
                entities["vessel"] = entity_text
            elif "PORT" in entity_label.upper():
                entities["port"] = entity_text
            elif "ETD" in entity_label.upper():
                entities["etd"] = entity_text
            elif "ETA" in entity_label.upper():
                entities["eta"] = entity_text
            elif "CY_DATE" in entity_label.upper():
                entities["cy_date"] = entity_text
            elif "RETURN_DATE" in entity_label.upper():
                entities["return_date"] = entity_text
            elif "DESTINATION" in entity_label.upper():
                entities["destination"] = entity_text
            # Add more mapping logic based on your specific entity labels

        return entities

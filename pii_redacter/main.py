from flask import Flask, request, jsonify
import torch
from transformers import AutoTokenizer, AutoModelForTokenClassification
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Global variables for model and tokenizer
model = None
tokenizer = None
device = None

def load_model():
    """Load the PII detection model and tokenizer"""
    global model, tokenizer, device
    
    try:
        model_name = "iiiorg/piiranha-v1-detect-personal-information"
        logger.info(f"Loading model: {model_name}")
        
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForTokenClassification.from_pretrained(model_name)
        
        # Set device
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model.to(device)
        
        logger.info(f"Model loaded successfully on device: {device}")
        
    except Exception as e:
        logger.error(f"Error loading model: {str(e)}")
        raise

def apply_redaction(masked_text, start, end, pii_type, aggregate_redaction):
    """Apply redaction to the specified range"""
    for j in range(start, end):
        masked_text[j] = ''
    if aggregate_redaction:
        masked_text[start] = '[REDACTED]'
    else:
        masked_text[start] = f'[{pii_type}]'

def mask_pii(text, aggregate_redaction=True):
    """Mask PII in the given text"""
    try:
        # Tokenize input text
        inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
        inputs = {k: v.to(device) for k, v in inputs.items()}
        
        # Get model predictions
        with torch.no_grad():
            outputs = model(**inputs)
        
        # Get predicted labels
        predictions = torch.argmax(outputs.logits, dim=-1)
        
        # Token offsets for redaction
        encoded_inputs = tokenizer.encode_plus(text, return_offsets_mapping=True, add_special_tokens=True)
        offset_mapping = encoded_inputs['offset_mapping']
        
        masked_text = list(text)
        is_redacting = False
        redaction_start = 0
        current_pii_type = ''
        
        for i, (start, end) in enumerate(offset_mapping):
            if start == end:  # Special token
                continue
            
            label = predictions[0][i].item()
            if label != model.config.label2id['O']:  # PII detected
                pii_type = model.config.id2label[label]
                if not is_redacting:
                    is_redacting = True
                    redaction_start = start
                    current_pii_type = pii_type
                elif not aggregate_redaction and pii_type != current_pii_type:
                    # End current redaction and start a new one
                    apply_redaction(masked_text, redaction_start, start, current_pii_type, aggregate_redaction)
                    redaction_start = start
                    current_pii_type = pii_type
            else:
                if is_redacting:
                    apply_redaction(masked_text, redaction_start, end, current_pii_type, aggregate_redaction)
                    is_redacting = False
        
        # Handle case where PII is at the end of the text
        if is_redacting:
            apply_redaction(masked_text, redaction_start, len(masked_text), current_pii_type, aggregate_redaction)
        
        return ''.join(masked_text)
        
    except Exception as e:
        logger.error(f"Error processing text: {str(e)}")
        raise

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "model_loaded": model is not None})

@app.route('/redact', methods=['POST'])
def redact_pii():
    """Redact PII from input text"""
    try:
        # Get JSON data from request
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({"error": "Missing 'text' field in request body"}), 400
        
        text = data['text']
        aggregate_redaction = data.get('aggregate_redaction', True)
        
        if not text or not isinstance(text, str):
            return jsonify({"error": "Text must be a non-empty string"}), 400
        
        # Process the text
        redacted_text = mask_pii(text, aggregate_redaction=aggregate_redaction)
        
        return jsonify({
            "original_text": text,
            "redacted_text": redacted_text,
            "aggregate_redaction": aggregate_redaction
        })
        
    except Exception as e:
        logger.error(f"Error in redact_pii: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    # Load model on startup
    load_model()
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=5000, debug=False)
    #text = "My name is Dhanushkumar and I live at Chennai. My phone number is +9190803470."
    #print(mask_pii(text, aggregate_redaction=True))

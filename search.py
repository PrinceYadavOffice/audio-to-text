import torch
from transformers import BertTokenizer, BertForSequenceClassification

# Load the fine-tuned BERT model and tokenizer
model_name = "bert-base-uncased"
tokenizer = BertTokenizer.from_pretrained(model_name)
model = BertForSequenceClassification.from_pretrained(model_name)

# Function to rank documents based on relevance to a search query
def rank_documents(query, documents):
    # Tokenize the query and documents and convert to input tensors
    input_ids = tokenizer.encode(query, documents, return_tensors="pt", padding=True, truncation=True)
    
    # Make prediction using the fine-tuned BERT model
    with torch.no_grad():
        outputs = model(input_ids)
        logits = outputs.logits
        relevance_scores = torch.softmax(logits, dim=1)[:, 1]  # Assuming the model is fine-tuned for binary relevance (0 or 1)

    # Get the ranked document indices
    ranked_indices = relevance_scores.argsort(descending=True)

    # Get the ranked documents based on the indices
    ranked_documents = [documents[idx] for idx in ranked_indices]

    return ranked_documents, relevance_scores

# Sample search query
search_query = "pizza toppings"

# Sample list of documents
documents = [
    "Pizza delivery near you.",
    "Make pizza in 30 minutes.",
    "Try these pizza toppings.",
    "Why pizza is everyone's favorite.",
    "pizza delivery boy"
]

# Rank the documents based on relevance to the search query
ranked_documents, relevance_scores = rank_documents(search_query, documents)


# Display the ranked documents and their relevance scores
print("Ranked Documents->")
for doc, score in zip(ranked_documents, relevance_scores):
    print(f"Document: {doc}\nRelevance Score: {score:.4f}\n")




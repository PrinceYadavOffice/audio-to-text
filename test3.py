from transformers import AutoTokenizer, AutoModel
from sklearn.metrics.pairwise import cosine_similarity
import torch


tokenizer = AutoTokenizer.from_pretrained('sentence-transformers/bert-base-nli-mean-tokens')
model = AutoModel.from_pretrained('sentence-transformers/bert-base-nli-mean-tokens')

def sentence_similarity(sentences):

    # initialize dictionary that will contain tokenized sentences
    tokens = {'input_ids': [], 'attention_mask': []}

    for sentence in sentences:
        # tokenize sentence and append to dictionary lists
        new_tokens = tokenizer.encode_plus(sentence, max_length=128, truncation=True,
                                        padding='max_length', return_tensors='pt')
        tokens['input_ids'].append(new_tokens['input_ids'][0])
        tokens['attention_mask'].append(new_tokens['attention_mask'][0])

    # reformat list of tensors into single tensor
    tokens['input_ids'] = torch.stack(tokens['input_ids'])
    tokens['attention_mask'] = torch.stack(tokens['attention_mask'])

    outputs = model(**tokens)
    embeddings = outputs.last_hidden_state
    attention_mask = tokens['attention_mask']
    mask = attention_mask.unsqueeze(-1).expand(embeddings.size()).float()
    masked_embeddings = embeddings * mask
    summed = torch.sum(masked_embeddings, 1)
    summed_mask = torch.clamp(mask.sum(1), min=1e-9)
    mean_pooled = summed / summed_mask
    # convert from PyTorch tensor to numpy array
    mean_pooled = mean_pooled.detach().numpy()

    # calculate
    similarity_aaray=cosine_similarity(
        [mean_pooled[0]],
        mean_pooled[1:]
    )

    similarity_aaray = similarity_aaray[0].tolist()
    similarity_dict = dict(zip(sentences[1:],similarity_aaray))

    return similarity_dict



sentences = [
    "How to make pizza at home?",
    "The best pizza recipe ever!",
    "fruit delivery near you.",
    "Make pizza in 30 minutes.",
    "Try these items toppings.",
    "Why pizza is everyone's favorite.",
]

result = sentence_similarity(sentences)


for key, value in result.items():
    print(f"key: {key} value: {value}")
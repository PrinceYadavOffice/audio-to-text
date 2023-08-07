from transformers import AutoTokenizer, AutoModel
import torch
from torch.nn.functional import normalize
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
from scipy.spatial import distance



tokenizer = AutoTokenizer.from_pretrained('sentence-transformers/bert-base-nli-mean-tokens')
model = AutoModel.from_pretrained('sentence-transformers/bert-base-nli-mean-tokens')



def sentence_similarity(sentences, model, tokenizer):
    # Tokenize all sentences in a single batch
    inputs = tokenizer(sentences, padding=True, truncation=True, return_tensors="pt", max_length=128)

    with torch.no_grad():
        # Forward pass through the model
        outputs = model(**inputs)
        embeddings = outputs.last_hidden_state

        # Normalize the embeddings
        embeddings = normalize(embeddings, p=2, dim=2)

        # Extract the embedding of the [CLS] token (representing the whole sentence)
        reference_embedding = embeddings[0][0]  # Shape: [embedding_size]

        # Compute the similarity with all other sentences
        similarity_list = []
        for emb in embeddings[1:]:
            sim_score = 1 - distance.cosine(reference_embedding.cpu(), emb[0].cpu())
            similarity_list.append(sim_score)

    # Create a dictionary with sentences and their corresponding similarity scores
    similarity_dict = dict(zip(sentences[1:], similarity_list))
    return similarity_dict



query = "what is going on with threads"

transcripts_sentences = [
    query
]
import os

current_directory = os.getcwd()
folder_path = os.path.join(current_directory, 'text_files')
dir_list = os.listdir(folder_path)
print(dir_list)

for text_file in dir_list:
    text_file_path = "text_files/"+text_file
    with open(text_file_path, 'r') as file:
        contents = file.read()
        transcripts_sentences.append(contents)

print(len(transcripts_sentences))

result = sentence_similarity(transcripts_sentences, model, tokenizer)

#creating data for excel
data_dict=dict(zip(dir_list, result.items()))

df = pd.DataFrame.from_dict(data_dict, orient='index', columns=['Sentence', 'similarity_value'])
df.insert(0, 'audio-file-slug', df.index)
df = df.sort_values(by = 'similarity_value',ascending = False)

most_similar_audio_file = df.iloc[0,0].split('.')[0]
print(f"similar audio: {most_similar_audio_file}")
# Save the DataFrame to Excel
# df = pd.DataFrame(list(result.items()), columns=['Sentence', 'similarity'])
# output_file = 'output.xlsx'
# df.to_excel(output_file, index=False)


for key, value in result.items():
    print(f"value: {value}")



df = pd.read_csv("csv_text_file.csv")
df = df.dropna() 
clean_senteces = [sentence.strip() for sentence in df['sentence'].tolist()]
# converting column data to list
csv_sentences=[query]
csv_sentences = csv_sentences + clean_senteces

del df

result_sentence = sentence_similarity(csv_sentences, model, tokenizer)

print(type(result_sentence))
# print(result_sentence)

sorted_dict = dict(sorted(result_sentence.items(), key = lambda x: x[1], reverse = True))


index=0
for key, value in sorted_dict.items():    
    print(key, " :",value)
    index+=1
    if index ==10:
        break


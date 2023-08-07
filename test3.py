from transformers import AutoTokenizer, AutoModel
from sklearn.metrics.pairwise import cosine_similarity
import torch, os
import pandas as pd
import json
import numpy as np


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



query = "what is going on with threads"

# transcripts_sentences = [
#     query
# ]


# current_directory = os.getcwd()
# folder_path = os.path.join(current_directory, 'text_files')
# dir_list = os.listdir(folder_path)
# print(dir_list)

# for text_file in dir_list:
#     text_file_path = "text_files/"+text_file
#     with open(text_file_path, 'r') as file:
#         contents = file.read()
#         transcripts_sentences.append(contents)

# print(len(transcripts_sentences))

# result = sentence_similarity(transcripts_sentences)

# #creating data for excel
# data_dict=dict(zip(dir_list, result.items()))

# df = pd.DataFrame.from_dict(data_dict, orient='index', columns=['Sentence', 'similarity_value'])
# df.insert(0, 'audio-file-slug', df.index)
# df = df.sort_values(by = 'similarity_value',ascending = False)

# most_similar_audio_file = df.iloc[0,0]
# print(f"similar audio: {most_similar_audio_file}")
# # Save the DataFrame to Excel
# # df = pd.DataFrame(list(result.items()), columns=['Sentence', 'similarity'])
# output_file = 'output.xlsx'
# df.to_excel(output_file, index=False)


# for key, value in result.items():
#     print(f"value: {value}")


df = pd.read_csv("csv_text_file.csv")
df = df.dropna() 
clean_senteces = [sentence.strip() for sentence in df['sentence'].tolist()]
# converting column data to list
csv_sentences=[query]
csv_sentences = csv_sentences + clean_senteces

del df

result_sentence = sentence_similarity(csv_sentences[:55])

print(type(result_sentence))

sorted_dict = dict(sorted(result_sentence.items(), key = lambda x: x[1], reverse = True))


i=0
for key, value in sorted_dict.items():    
    print(key[:], " :",value)
    i+=1
    if i==10:
        break

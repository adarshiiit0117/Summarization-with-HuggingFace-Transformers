# -*- coding: utf-8 -*-
"""Untitled4.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1mHvObFjk1XRmMJpP23dHixh7Yar5g0UI

Text summarization

IMPORT TOOLS
"""

import pandas as pd
from transformers  import T5Tokenizer, T5ForConditionalGeneration,Trainer,TrainingArguments

"""LOAD DATASET"""

train_df = pd.read_csv("/content/samsum-train.csv")
test_df = pd.read_csv("/content/samsum-test.csv")
train_df.head()

train_df.shape

train_df=train_df.sample(6000,random_state=42)
train_df.shape
test_df=test_df.sample(500,random_state=42)
test_df.shape

"""DATA PROCESSING"""

train_df['dialogue'][0]

import re
def clean_text(text):
    text = text.lower()
    text = re.sub(r'\[.*?\]', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text;
train_df['dialogue']=train_df['dialogue'].apply(clean_text)
train_df['summary']=train_df['summary'].apply(clean_text)
train_df

"""Tokenization"""

tokenizer = T5Tokenizer.from_pretrained("t5-small")
model = T5ForConditionalGeneration.from_pretrained("t5-small")

def preprocess_data(example):
  input_text = tokenizer(example['dialogue'],padding='max_length',truncation=True,max_length=512)
  target_text = tokenizer(example['summary'],padding='max_length',truncation=True,max_length=128)
  input_text['labels']=target_text['input_ids']
  return input_text
train_df=train_df.apply(preprocess_data,axis=1)
test_df=test_df.apply(preprocess_data,axis=1)

train_df[0]

"""FINE TUNING"""

model=T5ForConditionalGeneration.from_pretrained("t5-small")

# Define training arguments
training_args = TrainingArguments(
    output_dir="./results",          # output directory for checkpoints
    num_train_epochs=1,              # number of training epochs
    per_device_train_batch_size=2,   # batch size per device during training
    per_device_eval_batch_size=1,    # batch size for evaluation
    warmup_steps=50,                # number of warmup steps for learning rate scheduler
    weight_decay=0.01,               # strength of weight decay
    logging_dir="./logs",            # directory for storing logs
    logging_steps=5,                # how often to log training info
    save_steps=50,                  # how often to save a model checkpoint
    eval_steps=50,                   # how often to run evaluation
    evaluation_strategy="epoch",     # Ensure evaluation happens every `epoch`
)

train_df = train_df.reset_index(drop=True)
test_df = test_df.reset_index(drop=True)

trainer=Trainer(
    model=model,
    args=training_args,
    train_dataset=train_df,
    eval_dataset=test_df
)
trainer.train()

model.save_pretrained("./fine_tuned_model")
tokenizer.save_pretrained("./fine_tuned_model")

model=T5ForConditionalGeneration.from_pretrained("./fine_tuned_model")
tokenizer=T5Tokenizer.from_pretrained("./fine_tuned_model")

"""Summeriation system"""

device = model.device  # Get the device the model is on

def summarize_dialogue(dialogue):
    dialogue = clean_text(dialogue)  # Assuming clean_text is defined
    inputs = tokenizer(dialogue, return_tensors="pt", truncation=True, padding="max_length", max_length=512)

    # Move input tensors to the same device as the model
    inputs = {key: value.to(device) for key, value in inputs.items()}

    # Generate summary
    outputs = model.generate(
        inputs["input_ids"],
        max_length=150,
        num_beams=4,
        early_stopping=True
    )

    # Decode the generated summary
    summary = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return summary

# Test with a sample input
sample_dialogue = """
Violet: Hey Claire! I was reading an article about Austin and thought you might find it interesting!
Violet: It's about the current trends in urban development and how cities are planning for the future.
Violet: Here, let me share the link: <file_other>
Claire: Oh wow, that sounds like an insightful read. But I've actually already read that one last week.
Claire: It was really interesting though, especially the part about sustainable architecture in cities.
Claire: You know, I've been following these urban planning discussions for a while now.
Violet: Oh, I didn’t know that! Well, I’ll look for something else then, maybe something about eco-friendly cities or tech innovations.
Claire: That would be awesome! Let me know if you find something cool.
Violet: Sure, I’ll keep you posted. Thanks for the feedback!
"""

summary = summarize_dialogue(sample_dialogue)
print("Summary:", summary)

# Test with a dialogue on a different topic
sample_dialogue = """
John: Hey Sarah, have you seen the latest tech gadget reviews? I found this new smartwatch that's supposed to have amazing health tracking features.
John: It tracks heart rate, blood oxygen levels, sleep patterns, and even stress levels! It sounds like something right up your alley.
Sarah: That sounds really interesting! But I’ve been trying to cut down on tech distractions. I’ve heard these devices can be really overwhelming sometimes.
Sarah: I do think it’s cool that they can track so many health metrics though. I’m curious how accurate they really are.
John: Yeah, me too! There are also some new smartphones coming out with even better cameras and longer battery life. The new flagship model from XYZ brand has some insane specs.
Sarah: Ooh, I haven’t kept up with phones recently, but I’ve heard the camera quality is getting ridiculously good. It’s almost like a professional camera in your pocket now!
Sarah: Still, I feel like I’m fine with my current phone for now. I don’t really feel the need to upgrade unless something really groundbreaking comes out.
John: Totally understand that. It’s the same with me. But I think the battery life improvements are enough to make me consider it. I hate running out of battery when I’m out and about.
Sarah: That’s fair! I’m always worried about battery life too. Honestly, I think phones should last at least two full days on a single charge by now.
John: I agree! It’s so annoying when your phone dies in the middle of the day. I wonder if we’ll ever get to a point where we don’t have to charge our phones every day.
Sarah: That would be amazing! I think as tech improves, battery tech might also catch up. Let’s hope the next generation of phones can last longer!
"""

summary = summarize_dialogue(sample_dialogue)
print("Summary:", summary)

"""Download Model to your machine"""

import shutil

# Path to the directory containing the fine-tuned model
model_dir = "./fine_tuned_model"

# Output zip file path
output_zip_path = "saved_summary_model.zip"

# Create a zip archive
shutil.make_archive(base_name="saved_summary_model", format="zip", root_dir=model_dir)

from IPython.display import FileLink

# Display a download link
FileLink(output_zip_path)
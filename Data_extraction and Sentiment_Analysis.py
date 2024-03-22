#!/usr/bin/env python
# coding: utf-8

# ## Data_Extraction

# In[1]:


import csv
import requests
import pandas as pd
from bs4 import BeautifulSoup
import os

# Function to scrape data from a single website
def scrape_website(url):
    try:
        # Send a GET request to the URL
        response = requests.get(url)
        
        # Check if the request was successful
        if response.status_code == 200:
            # Parse the HTML content of the page
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract the article text from within the body tag
            body_content = soup.find('body')
            if body_content:
                # Remove unwanted elements such as scripts and styles
                [x.extract() for x in body_content(['script', 'style'])]
                # Extract the text
                article_text = body_content.get_text(separator='\n', strip=True)
                
                # Return the article text
                return article_text
            else:
                return "Failed to find body content"
        else:
            return f"Failed to scrape: HTTP status code {response.status_code}",
    except Exception as e:
        return f"Failed to scrape: {e}",

# Read the CSV file containing website URLs
csv_file = 'C:\\Users\\saiku\\Desktop\\Black coffee\\Input.xlsx - Sheet1.csv'  # Replace with the path to your CSV file
output_folder = 'C:\\Users\\saiku\\Desktop\\Scraped_Text_Files'  # Replace with the path to the output folder

# Create the output folder if it doesn't exist
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Open the CSV file and read the URLs from the second column
with open(csv_file, 'r', newline='') as file:
    reader = csv.reader(file)
    next(reader)  # Skip header row if it exists
    for row in reader:
        website_id = row[0]  # Assuming the URL IDs are in the first column
        website_url = row[1]  # Assuming the URLs are in the second column
        print("Scraping:", website_url)
        article_text = scrape_website(website_url)
        if isinstance(article_text, tuple):  # Check if article_text is a tuple (error message)
            print(f"Failed to scrape URL {website_url}: {article_text[0]}")
        else:
            # Write the scraped text to a text file
            filename = os.path.join(output_folder, f"{website_id}.txt")
            with open(filename, 'w', encoding='utf-8') as text_file:
                text_file.write(article_text)
            print(f"Scraped data saved to: {filename}")
        print()


# # Sentimental_Analysis

# ### Cleaning using Stop Words Lists

# In[19]:


import os
from nltk.tokenize import word_tokenize

# Function to read stop words from multiple files and combine them into a set
def read_stop_words(stop_words_files):
    combined_stop_words = set()
    for stop_words_file in stop_words_files:
        with open(stop_words_file, 'r', encoding='utf-8', errors='ignore') as f:  # Ignore errors while decoding
            words = set(f.read().splitlines())
            combined_stop_words.update(words)
    return combined_stop_words

# Function to clean text files by removing stop words
def clean_text_files(text_files_folder, stop_words, cleaned_files_folder):
    # Create the folder if it doesn't exist
    if not os.path.exists(cleaned_files_folder):
        os.makedirs(cleaned_files_folder)
    
    for filename in os.listdir(text_files_folder):
        if filename.endswith('.txt'):
            input_file_path = os.path.join(text_files_folder, filename)
            output_file_path = os.path.join(cleaned_files_folder, filename)
            
            # Read the content of the text file
            with open(input_file_path, 'r', encoding='utf-8', errors='ignore') as f:  # Ignore errors while decoding
                text = f.read()
            
            # Tokenize the text into words
            words = word_tokenize(text)
            
            # Remove stop words from the tokenized words
            filtered_words = [word for word in words if word.lower() not in stop_words]
            
            # Reconstruct the cleaned text
            cleaned_text = ' '.join(filtered_words)
            
            # Save the cleaned text to a new file
            with open(output_file_path, 'w', encoding='utf-8') as f:
                f.write(cleaned_text)

# Path to the folder containing text files
text_files_folder = 'C:\\Users\\saiku\\Desktop\\Black coffee\\Scraped_Text_Files'

# Paths to the stop words files
stop_words_files = [
    'C:\\Users\\saiku\\Desktop\\Black coffee\\stopword_file\\StopWords_Auditor.txt',
    'C:\\Users\\saiku\\Desktop\\Black coffee\\stopword_file\\StopWords_Currencies.txt',
    'C:\\Users\\saiku\\Desktop\\Black coffee\\stopword_file\\StopWords_DatesandNumbers.txt',
    'C:\\Users\\saiku\\Desktop\\Black coffee\\stopword_file\\StopWords_Generic.txt',
    'C:\\Users\\saiku\\Desktop\\Black coffee\\stopword_file\\StopWords_GenericLong.txt',
    'C:\\Users\\saiku\\Desktop\\Black coffee\\stopword_file\\StopWords_Geographic.txt',
    'C:\\Users\\saiku\\Desktop\\Black coffee\\stopword_file\\StopWords_Names.txt',
]

# Path to the folder where cleaned text files will be saved
cleaned_files_folder = 'C:\\Users\\saiku\\Desktop\\Black coffee\\Cleaned_Text_Files'

# Read stop words from multiple files
stop_words = read_stop_words(stop_words_files)

# Clean text files by removing stop words
clean_text_files(text_files_folder, stop_words, cleaned_files_folder)

print("Text files cleaned successfully and saved to:", cleaned_files_folder)


# ## Creating dictionary of Positive and Negative words

# In[1]:


def read_words_from_file(file_path):
    with open(file_path, 'r') as file:
        words = file.read().splitlines()
    return words

# Path to the text files containing positive and negative words
positive_words_file = 'C:\\Users\\saiku\\Desktop\\Black coffee\\MasterDictionary\\positive-words.txt'
negative_words_file = 'C:\\Users\\saiku\\Desktop\\Black coffee\\MasterDictionary\\negative-words.txt'

# Read positive and negative words from files
positive_words = read_words_from_file(positive_words_file)
negative_words = read_words_from_file(negative_words_file)

# Create dictionaries of positive and negative words
positive_dict = {word: True for word in positive_words}
negative_dict = {word: True for word in negative_words}

print("Positive words dictionary:", positive_dict)
print("Negative words dictionary:", negative_dict)


# In[7]:


import os
import re
import nltk
import pandas as pd
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import cmudict

# Load CMU Pronouncing Dictionary for syllable count
nltk.download('cmudict')
d = cmudict.dict()

# Function to count syllables in a word using CMU Pronouncing Dictionary
def syllable_count(word):
    try:
        return [len(list(y for y in x if y[-1].isdigit())) for x in d[word.lower()]][0]
    except KeyError:
        return 0  # Return 0 if the word is not found in the dictionary

# Function to calculate complex word count
def count_complex_words(words):
    complex_word_count = 0
    for word in words:
        if syllable_count(word) > 2:  # Consider words with more than 2 syllables as complex
            complex_word_count += 1
    return complex_word_count

# Function to calculate personal pronouns count
def count_personal_pronouns(text):
    pronouns = re.findall(r'\b(I|we|my|ours|us)\b', text, flags=re.IGNORECASE)
    return len(pronouns)

# Function to calculate readability metrics
def calculate_readability_metrics(text):
    sentences = sent_tokenize(text)
    words = word_tokenize(text)
    word_count = len(words)
    sentence_count = len(sentences)
    
    # Check if word count or sentence count is zero to avoid division by zero
    if word_count == 0 or sentence_count == 0:
        avg_sentence_length = 0
        percentage_complex_words = 0
        fog_index = 0
        avg_words_per_sentence = 0
    else:
        avg_sentence_length = word_count / sentence_count
        percentage_complex_words = count_complex_words(words) / word_count
        fog_index = 0.4 * (avg_sentence_length + percentage_complex_words)
        avg_words_per_sentence = word_count / sentence_count
    
    return avg_sentence_length, percentage_complex_words, fog_index, avg_words_per_sentence


# Function to analyze sentiment and calculate scores
def analyze_sentiment(text, positive_dict, negative_dict):
    words = word_tokenize(text)
    word_count = len(words)
    positive_score = sum(1 for word in words if word in positive_dict)
    negative_score = sum(1 for word in words if word in negative_dict)
    polarity_score = (positive_score - negative_score) / (positive_score + negative_score + 0.000001)
    subjectivity_score = (positive_score + negative_score) / (word_count + 0.000001)
    avg_sentence_length, percentage_complex_words, fog_index, avg_words_per_sentence = calculate_readability_metrics(text)
    complex_word_count = count_complex_words(words)
    personal_pronouns_count = count_personal_pronouns(text)
    
    # Handle division by zero error for average word length
    if word_count == 0:
        avg_word_length = 0
    else:
        avg_word_length = sum(len(word) for word in words) / word_count
    
    # Handle division by zero error for syllable per word
    if word_count == 0:
        syllable_per_word = 0
    else:
        syllable_per_word = sum(syllable_count(word) for word in words) / word_count
    
    return {
        'Positive Score': positive_score,
        'Negative Score': negative_score,
        'Polarity Score': polarity_score,
        'Subjectivity Score': subjectivity_score,
        'Avg Sentence Length': avg_sentence_length,
        'Percentage of Complex Words': percentage_complex_words,
        'Fog Index': fog_index,
        'Avg Words Per Sentence': avg_words_per_sentence,
        'Complex Word Count': complex_word_count,
        'Word Count': word_count,
        'Syllable Per Word': syllable_per_word,
        'Personal Pronouns': personal_pronouns_count,
        'Avg Word Length': avg_word_length
    }

# Path to the folder containing cleaned text files
cleaned_files_folder = 'C:\\Users\\saiku\\Desktop\\Black coffee\\Cleaned_Text_Files'

# Path to the output CSV file
output_csv_file = 'sentiment_analysis_results.csv'


# Process each cleaned text file
results = []
for filename in os.listdir(cleaned_files_folder)[:100]:  # Process only first 100 files
    if filename.endswith('.txt'):
        file_path = os.path.join(cleaned_files_folder, filename)
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()
        sentiment_scores = analyze_sentiment(text, positive_dict, negative_dict)
        results.append(sentiment_scores)

# Write results to CSV file
import csv
with open(output_csv_file, 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['File Name'] + list(results[0].keys())
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for i, result in enumerate(results):
        writer.writerow({'File Name': f'File_{i+1}'} | result)


# In[ ]:





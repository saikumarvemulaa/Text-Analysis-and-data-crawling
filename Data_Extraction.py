#!/usr/bin/env python
# coding: utf-8

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


# In[ ]:





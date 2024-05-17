#Multiple Url we can use Using this
# Import necessary libraries
import requests  # For making HTTP requests to fetch web pages
from bs4 import BeautifulSoup  # For parsing HTML and XML documents
import csv  # For reading and writing CSV files
import datetime  # For working with dates and times
import time  # For adding delays
import pandas as pd  # For data manipulation and analysis
import smtplib  # For sending emails using the Simple Mail Transfer Protocol
from email.mime.text import MIMEText  # For creating text MIME objects for email
from email.mime.multipart import MIMEMultipart  # For creating multipart MIME objects for email
from email.mime.base import MIMEBase  # For base class for MIME attachments
from email import encoders  # For encoding email attachments
import matplotlib.pyplot as plt  # For creating static, animated, and interactive visualizations
import os  # For interacting with the operating system

# List of product URLs and their desired price thresholds
products = [
    {'url': 'https://www.amazon.in/DUDEME-Programmers-Kisses-Programmer-Developer/dp/B08GCXV1TK/ref=sr_1_7?sr=8-7', 'threshold': 449},
    # Add more products here with their URLs and price thresholds
]

# Email credentials
EMAIL_ADDRESS = 'sohankrshah000@gmail.com'
EMAIL_PASSWORD = 'your_password'  # Replace with your email password

def send_mail(subject, body):
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)  # Connect to the Gmail SMTP server using SSL
    server.ehlo()  # Identify ourselves to the SMTP server
    server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)  # Login to the email account
    
    msg = MIMEMultipart()  # Create a multipart MIME object
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = EMAIL_ADDRESS
    msg['Subject'] = subject
    
    msg.attach(MIMEText(body, 'plain'))  # Attach the email body to the MIME object

    server.sendmail(EMAIL_ADDRESS, EMAIL_ADDRESS, msg.as_string())  # Send the email
    server.quit()  # Disconnect from the SMTP server

def plot_price_history(product_name):
    df = pd.read_csv('AmazonwebscraperDataSet.csv')  # Read the CSV file into a DataFrame
    df = df[df['Title'] == product_name]  # Filter the DataFrame for the specific product
    plt.plot(df['Date'], df['Price'])  # Plot the price history
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.title(f'Price History for {product_name}')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f'{product_name}_price_history.png')  # Save the plot as an image file
    plt.close()

def check_product(url, threshold):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Brave/91.0.4472.124'
    }
    try:
        page = requests.get(url, headers=headers)  # Fetch the page content
        page.raise_for_status()  # Raise an HTTPError for bad responses
    except requests.RequestException as e:
        log_error(f"Error fetching the page: {e}")  # Log the error
        return

    soup = BeautifulSoup(page.content, "html.parser")  # Parse the page content

    title_element = soup.find(id='productTitle')  # Find the product title
    if title_element:
        title = title_element.get_text().strip()
    else:
        title = "Title not found"

    price_parent_element = soup.find('span', {'class': 'a-price'})  # Find the price parent element
    if price_parent_element:
        price_element = price_parent_element.find('span', {'class': 'a-price-whole'})  # Find the whole price element
        if price_element:
            price = price_element.get_text().strip().replace(',', '')  # Get the price and remove commas
            try:
                price = int(price)  # Convert the price to an integer
            except ValueError:
                log_error(f"Price conversion error: {price}")  # Log conversion error
                price = "Price not found"
        else:
            price = "Price not found"
    else:
        price = "Price not found"

    today = datetime.date.today()  # Get the current date
    data = [title, price, today]  # Prepare the data to be written to the CSV file

    # Writing the header only if the file does not exist
    try:
        with open('AmazonwebscraperDataSet.csv', 'x', newline='', encoding='UTF8') as f:
            writer = csv.writer(f)
            writer.writerow(['Title', 'Price', 'Date'])  # Write the header
    except FileExistsError:
        pass

    # Appending the data to the CSV file
    with open('AmazonwebscraperDataSet.csv', 'a+', newline='', encoding='UTF8') as f:
        writer = csv.writer(f)
        writer.writerow(data)  # Write the data

    if isinstance(price, int) and price < threshold:  # Check if the price is below the threshold
        previous_price = get_previous_price(title)
        if previous_price and previous_price != "Price not found":
            price_diff = previous_price - price
            subject = f"Price Drop Alert: {title}"
            body = (f"The price for {title} has dropped to {price} (₹{price_diff} less).\n\n"
                    f"Check it out here: {url}")
        else:
            subject = f"Price Drop Alert: {title}"
            body = (f"The price for {title} has dropped to {price}.\n\n"
                    f"Check it out here: {url}")
        
        send_mail(subject, body)  # Send the email notification
        plot_price_history(title)  # Plot the price history

def get_previous_price(title):
    try:
        df = pd.read_csv('AmazonwebscraperDataSet.csv')  # Read the CSV file into a DataFrame
        df = df[df['Title'] == title]  # Filter the DataFrame for the specific product
        if not df.empty:
            return df.iloc[-1]['Price']  # Return the last recorded price
    except FileNotFoundError:
        return "Price not found"
    return "Price not found"

def log_error(error_message):
    with open('error_log.txt', 'a') as f:
        f.write(f"{datetime.datetime.now()}: {error_message}\n")  # Log the error with timestamp

def check():
    for product in products:
        check_product(product['url'], product['threshold'])  # Check each product

while True:
    check()  # Run the check function
    time.sleep(86400)  # Check once a day (86400 seconds)

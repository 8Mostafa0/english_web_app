import requests
from bs4 import BeautifulSoup
import time
import csv

# Base URL for Magoosh TOEFL Blog
base_url = "https://magoosh.com/toefl/"

# Headers to mimic a browser (reduces chance of being blocked)
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# Function to scrape blog post links from the main TOEFL blog page
def get_post_links(url):
    try:
        # Send request to the page
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Check for request errors
        soup = BeautifulSoup(response.text, "html.parser")

        # Find all post links (adjust selector based on Magoosh's HTML structure)
        # Inspect magoosh.com/toefl to find the right class or tag
        post_links = []
        for article in soup.find_all("h2", class_="post-title"):  # Example class, may need adjustment
            link = article.find("a")
            if link and link["href"]:
                post_links.append(link["href"])

        return post_links
    except Exception as e:
        print(f"Error fetching links: {e}")
        return []

# Function to scrape content from an individual blog post
def scrape_post_content(post_url):
    try:
        response = requests.get(post_url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Extract title
        title = soup.find("h1", class_="post-title")  # Adjust class as needed
        title = title.get_text(strip=True) if title else "No title"

        # Extract main content (e.g., paragraphs in the post body)
        content = ""
        content_div = soup.find("div", class_="post-content")  # Adjust class as needed
        if content_div:
            paragraphs = content_div.find_all("p")
            content = "\n".join([p.get_text(strip=True) for p in paragraphs])

        return {"title": title, "url": post_url, "content": content}
    except Exception as e:
        print(f"Error scraping {post_url}: {e}")
        return None

# Main function to scrape and save data
def main():
    print("Scraping Magoosh TOEFL Blog...")
    
    # Get all post links from the main blog page
    post_links = get_post_links(base_url)
    if not post_links:
        print("No posts found. Check URL or HTML structure.")
        return

    # Store scraped data
    scraped_data = []
    
    # Scrape each post (limit to avoid overwhelming the server)
    for link in post_links[:10]:  # Limit to 10 posts for testing; remove limit for all
        print(f"Scraping {link}...")
        post_data = scrape_post_content(link)
        if post_data:
            scraped_data.append(post_data)
        time.sleep(2)  # Delay to respect server (adjust as needed)

    # Save to CSV for bot use
    with open("magoosh_toefl_data.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["title", "url", "content"])
        writer.writeheader()
        writer.writerows(scraped_data)

    print(f"Scraped {len(scraped_data)} posts. Saved to magoosh_toefl_data.csv")

# Run the scraper
if __name__ == "__main__":
    main()
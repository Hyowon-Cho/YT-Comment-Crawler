# The Youtube comments Crawler 


### 💻 Python, BeautifulSoup, Selenium

#

### Libraries
- BeautifulSoup
- Selenium
- pandas
- requests

#

### About Codes

### 💻 get_urls_from_youtube_with_keyword(keyword) 
- A function that crawls the YouTube video title and URL for the desired keyword

### 💻 get_channel_video_url_list 
- A function that crawls the YouTube video title and URL for the desired channel

### 💻 crawl_youtube_page_html_sources(urls) 
- Each URL is accessed by Selenium and scrolls so that all comments can be loaded, and when scrolling is over, the HTML code is crawled and returned to the list

### 💻 get_user_IDs_and_comments(url_dict, video_type, html_source) 
- Extracted only the comment data portion from each page source code
- After extraction for the ID value and the comment part from the review data, the extraction result for each page is made into a dictionary form and then returned.

### 💻 convert_crawl_result_dict_to_csv(crawl_result_dict) 
- Makes extraction results in dataframe format
- Saving each dataframe as a csv file using a title that removes special characters from the titles of titles as the name of the csv file

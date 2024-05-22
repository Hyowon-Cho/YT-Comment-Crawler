from selenium import webdriver as wd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import pandas as pd
import requests
import re


def check_comment_count_is_zero(html_source, css_selector):
    is_comment_count_zero = False
    
    soup = BeautifulSoup(html_source, 'lxml')
    
    datas = soup.select(css_selector)
    
    if len(datas) > 0:
        comment_count_data = datas[0]
        
        if comment_count_data.text == "Comment 0":
            is_comment_count_zero = True
            
    return is_comment_count_zero


def scroll(driver, height=700):
    driver.execute_script(f"window.scrollTo(0, {height});")



def scroll_page(driver):
    last_page_height = driver.execute_script("return document.documentElement.scrollHeight")

    while True:
        driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
        
        time.sleep(3.0)
        
        
        new_page_height = driver.execute_script("return document.documentElement.scrollHeight")
        
        if new_page_height == last_page_height:
            break
            
        last_page_height = new_page_height

    return driver


def get_url_title_in_html_source(html_source, css_selector):
    titles, urls = [], []
    
    soup = BeautifulSoup(html_source, 'lxml')
    
    datas = soup.select(css_selector)
    
    for data in datas:
        title = data.text.replace('\n', '')
        url = "https://www.youtube.com" + data.get('href')
        
        titles.append(title)
        urls.append(url)
        
    return titles, urls


def divide_watch_shorts(titles, urls):
    watch_url, shorts_url = [], []
    
    for title, url in zip(titles, urls):
        url_type = url.split("/")[3].split("?")[0]
        
        if url_type == "watch":
            watch_url.append({
                "title": title, 
                "url": url
            })
        elif url_type == "watch":
            shorts_url.append({
                "title": title, 
                "url": url
            })
            
    return watch_url, shorts_url
        


def get_urls_from_youtube_with_keyword(keyword):
    
    search_keyword_encode = requests.utils.quote(keyword)
    
    url = "https://www.youtube.com/results?search_query=" + search_keyword_encode
    
    driver = wd.Chrome(executable_path="/Users/donghyunjang/PythonHome/chromedriver_105")
    driver.maximize_window()
    
    driver.get(url)
    
    driver = scroll_page(driver=driver)
        
    html_source = driver.page_source
    
    driver.quit()
    
    css_selector = "ytd-video-renderer.style-scope.ytd-item-section-renderer > div#dismissible > div.text-wrapper.style-scope.ytd-video-renderer > div#meta > div#title-wrapper > h3.title-and-badge.style-scope.ytd-video-renderer > a#video-title"
    
    titles, urls = get_url_title_in_html_source(
        html_source=html_source,
        css_selector=css_selector
    )
        
    return titles, urls


def get_channel_video_url_list(channel_url):
    titles = []
    urls = []
    
    driver = wd.Chrome(executable_path="/Users/donghyunjang/PythonHome/chromedriver_105")
    driver.maximize_window()
    
    driver.get(channel_url)
    
    driver = scroll_page(driver=driver)
        
    html_source = driver.page_source
    
    driver.quit()
    
    url_title_css_selector = "ytd-grid-video-renderer.style-scope.ytd-grid-renderer > div#dismissible > div#details > div#meta > h3.style-scope.ytd-grid-video-renderer > a#video-title"
    
    titles, urls = get_url_title_in_html_source(
        html_source=html_source, 
        css_selector=url_title_css_selector
    )
        
    return titles, urls

def crawl_youtube_page_html_sources(urls):
    html_sources = []

    for idx in range(len(urls)):
        driver = wd.Chrome(executable_path="/Users/donghyunjang/PythonHome/chromedriver_105")
        driver.maximize_window()
        driver.get(urls[idx]['url'])
        
        time.sleep(3.0)
        
        scroll(driver)
        
        comment_css_selector = "ytd-comments-header-renderer.style-scope.ytd-item-section-renderer > div#title > h2#count > yt-formatted-string.count-text.style-scope.ytd-comments-header-renderer"
        
        WebDriverWait(driver, 100).until(EC.presence_of_element_located((By.CSS_SELECTOR, comment_css_selector)))
        
        html_source = driver.page_source
        
        is_comment_count_zero = check_comment_count_is_zero(
            html_source=html_source, css_selector=comment_css_selector
        )
        
        if not is_comment_count_zero:
            driver = scroll_page(driver=driver)

        html_source = driver.page_source
        html_sources.append(html_source)

        driver.quit()
        
    return html_sources


def post_processing_text(text):
    return text.replace('\n', '').replace('\t', '').replace('                ','') if text is not None else ""


def pack_space(text):
    return " ".join(text.split())


def get_user_IDs_and_comments(url_dict, video_type, html_source):
    comment_crawl_result_dict = {
        "title": url_dict['title'], 
        "video_url": url_dict['url'], "video_type": video_type,
        "comment": []
    }
    
    comment_id_css_selector = "ytd-comment-renderer#comment > div#body > div#main > div#header > div#header-author > h3.style-scope.ytd-comment-renderer > a#author-text"
    comment_text_css_selector = "ytd-comment-renderer#comment > div#body > div#main > div#comment-content > ytd-expander#expander > div#content > yt-formatted-string#content-text"
    soup = BeautifulSoup(html_source, 'lxml')


    youtube_user_ID_list = soup.select(comment_id_css_selector)
    youtube_comment_list = soup.select(comment_text_css_selector)

    for youtube_user_id, youtube_comment in zip(youtube_user_ID_list, youtube_comment_list):
        user_id = pack_space(text=post_processing_text(text=youtube_user_id.text))
        comment = post_processing_text(text=youtube_comment.text)

        comment_data_dict = {"id":user_id, "comment":comment}
        
        comment_crawl_result_dict['comment'].append(comment_data_dict)
    
    return comment_crawl_result_dict


def convert_crawl_result_dict_to_csv(crawl_result_dict):
    title = re.sub('[-=+,#/\?:^$.@*\"※~&%ㆍ!』\\‘|\(\)\[\]\<\>`\'…《\》]', '', crawl_result_dict['title'])
    
    temp_df = pd.DataFrame(crawl_result_dict['comment'])
    
    temp_df = temp_df[['id', 'comment']]
    
    temp_df.to_csv(f"{title}.csv", index=False)    

import time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

def select_dropdown_option_by_index(select_element, index):
    options = select_element.find_elements(By.TAG_NAME, 'option')
    if index < len(options):
        options[index].click()
    else:
        raise ValueError(f"Index '{index}' is out of bounds for dropdown options")

def scrape_nueplex(driver):
    site_ids = ['1', '2']
    site_names = {'1': 'DHA', '2': 'Askari IV'}

    for site_id in site_ids:
        driver.get("https://nueplex.com/")
        wait = WebDriverWait(driver, 10)

        site_dropdown = Select(wait.until(EC.presence_of_element_located((By.ID, 'branch'))))
        select_dropdown_option_by_index(site_dropdown, int(site_id))
        
        movie_dropdown = Select(wait.until(EC.presence_of_element_located((By.ID, 'dateShowMovie'))))
        select_dropdown_option_by_index(movie_dropdown, 1)
        
        date_dropdown = Select(wait.until(EC.presence_of_element_located((By.ID, 'dateShowTime'))))
        select_dropdown_option_by_index(date_dropdown, 0)

        time.sleep(3)
        
        showtimes = driver.find_elements(By.CLASS_NAME, 'movie-shedule')
        for showtime in showtimes:
            title = showtime.find_element(By.TAG_NAME, 'h4').text.strip()
            times = showtime.find_elements(By.CLASS_NAME, 'time')
            for time_element in times:
                time_text = time_element.text.strip()
                date_text = showtime.find_element(By.CLASS_NAME, 'session-date').text.strip()
                print(f"Nueplex data: {site_names[site_id]}, Date: {date_text}, Time: {time_text}")

def scrape_cinepax(driver):
    cinepax_urls = [
        ("AMANAH MALL LAHORE", "https://cinepax.com/Browsing/Cinemas/Details/0000000012"),
        ("BOULEVARD MALL HYDERABAD", "https://cinepax.com/Browsing/Cinemas/Details/0000000010"),
        ("HOTELONE FAISALABAD", "https://cinepax.com/Browsing/Cinemas/Details/0000000004"),
        ("JINNAH PARK RAWALPINDI", "https://cinepax.com/Browsing/Cinemas/Details/0000000003"),
        ("KINGS MALL GUJRANWALA", "https://cinepax.com/Browsing/Cinemas/Details/0000000006"),
        ("LAKE CITY LAHORE", "https://cinepax.com/Browsing/Cinemas/Details/0000000007"),
        ("MALL OF SIALKOT", "https://cinepax.com/Browsing/Cinemas/Details/0000000013"),
        ("NAYYAR MALL GUJRAT", "https://cinepax.com/Browsing/Cinemas/Details/0000000009"),
        ("OCEAN MALL KARACHI", "https://cinepax.com/Browsing/Cinemas/Details/0000000002"),
        ("PACKAGES MALL LAHORE", "https://cinepax.com/Browsing/Cinemas/Details/0000000014"),
        ("WORLD TRADE CENTER ISLAMABAD", "https://cinepax.com/Browsing/Cinemas/Details/0000000011")
    ]

    for cinema_name, url in cinepax_urls:
        print(f"Scraping {cinema_name} ({url})")
        driver.get(url)
        time.sleep(5)  # Wait for the page to load completely
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        showtimes_divs = soup.find_all('div', class_='session')
        for div in showtimes_divs:
            date = div.find('h4', class_='session-date').text.strip()
            times = div.find_all('time')
            for time_element in times:
                time_text = time_element.text.strip()
                print(f"Cinepax data: {cinema_name}, Date: {date}, Time: {time_text}")

def scrape_mecinemas(driver):
    cinema_urls = [
        ("Karachi Atrium Cinemas", "https://www.mecinemas.com/movie_details.php?code=HO00001264")
    ]

    for cinema_name, cinema_url in cinema_urls:
        print(f"Scraping {cinema_name} ({cinema_url})")
        driver.get(cinema_url)
        time.sleep(5)  # Wait for the page to load completely
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        showtimes_div = soup.find('div', class_='showtimes')
        if showtimes_div:
            header = showtimes_div.find('h4')
            if header:
                header_text = header.get_text(strip=True)
                date_start = header_text.find("Showtimes") + len("Showtimes")
                date_end = header_text.find(" at ")
                show_date = header_text[date_start:date_end].strip()
                times = showtimes_div.find_all('span', class_='available')
                for time_span in times:
                    time_text = time_span.get_text(strip=True)
                    print(f"Mecinemas data: {cinema_name}, Date: {show_date}, Time: {time_text}")

def main():
    driver = webdriver.Chrome()
    try:
        scrape_nueplex(driver)
        scrape_cinepax(driver)
        scrape_mecinemas(driver)
    finally:
        driver.quit()

if __name__ == "__main__":
    main()

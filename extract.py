import time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

def select_dropdown_option_by_text(dropdown, text):
    """Select an option from a dropdown by its visible text."""
    options = dropdown.options
    for option in options:
        if option.text.strip() == text:
            dropdown.select_by_visible_text(text)
            return
    raise ValueError(f"Option with text '{text}' not found in dropdown")

def select_default_date(date_dropdown):
    """Select the default date from the dropdown (the first option)."""
    default_date = date_dropdown.options[0].text.strip()  # Index 0 is the default date
    date_dropdown.select_by_index(0)
    return default_date

def scrape_nueplex(driver):
    driver.get('https://nueplex.com/')
    time.sleep(5)
    wait = WebDriverWait(driver, 20)
    site_dropdown = Select(wait.until(EC.presence_of_element_located((By.ID, 'branch'))))
    site_ids = [option.get_attribute('value') for option in site_dropdown.options if option.get_attribute('value') != 'All']
    location_map = {'1': 'DHA', '2': 'Askari IV'}
    for site_id in site_ids:
        location = location_map.get(site_id, 'Unknown Location')
        print(f"Selecting site with ID: {site_id}")
        select_dropdown_option_by_text(site_dropdown, site_dropdown.options[int(site_id)].text)
        time.sleep(3)
        site_dropdown = Select(wait.until(EC.presence_of_element_located((By.ID, 'branch'))))
        cinema_dropdown = Select(wait.until(EC.presence_of_element_located((By.ID, 'dateShowCinema'))))
        movie_dropdown = Select(wait.until(EC.presence_of_element_located((By.ID, 'dateShowMovie'))))
        date_dropdown = Select(wait.until(EC.presence_of_element_located((By.ID, 'dateShowTime'))))
        select_dropdown_option_by_text(cinema_dropdown, "ALL CINEMAS")
        time.sleep(1)
        movie_dropdown = Select(wait.until(EC.presence_of_element_located((By.ID, 'dateShowMovie'))))
        select_dropdown_option_by_text(movie_dropdown, "NA BALIGH AFRAAD (PAKISTANI)")
        time.sleep(1)
        date_dropdown = Select(wait.until(EC.presence_of_element_located((By.ID, 'dateShowTime'))))
        default_date = select_default_date(date_dropdown)
        print(f"Selecting date: {default_date}")
        time.sleep(1)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        showings = soup.find_all('div', class_='movie-shedule')
        for showing in showings:
            title_element = showing.find('h4', class_='eq-height')
            time_element = showing.find('span', class_='time')
            if title_element and time_element:
                title_text = title_element.get_text(strip=True)
                time_text = time_element.get_text(strip=True)
                print(f"Nueplex data: {location}, Date: {default_date}, Time: {time_text}")

def scrape_cinepax(driver):
    driver.get('https://cinepax.com/')
    time.sleep(5)
    cinema_links = [
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

    for cinema_name, cinema_url in cinema_links:
        print(f"Scraping {cinema_name} ({cinema_url})")
        driver.get(cinema_url)
        time.sleep(5)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        showtimes_containers = soup.find_all('div', class_='film-showtimes')
        for container in showtimes_containers:
            film_title = container.find('h3', class_='film-title')
            if film_title and 'Na Baligh Afraad' in film_title.text:
                session_dates = container.find_all('h4', class_='session-date')
                if session_dates:
                    date_text = session_dates[0].get_text(strip=True)  # Only take the first date
                    session_times = session_dates[0].find_next('div', class_='session-times')
                    times = session_times.find_all('time')
                    for time_elem in times:
                        time_text = time_elem.get_text(strip=True)
                        print(f"Cinepax data: {cinema_name}, Date: {date_text}, Time: {time_text}")
                break  # Only scrape the first date, then move to the next cinema

def main():
    driver = webdriver.Chrome()
    try:
        scrape_nueplex(driver)
        scrape_cinepax(driver)
    finally:
        driver.quit()

if __name__ == "__main__":
    main()

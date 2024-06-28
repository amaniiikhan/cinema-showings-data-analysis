import time
import mysql.connector
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from datetime import datetime

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

def convert_date_to_uniform_format(date_str):
    """Convert date to 'YYYY-MM-DD' format."""
    for date_format in ('%A, %d %B %Y', '%d-%b-%Y'):
        try:
            date_obj = datetime.strptime(date_str, date_format)
            return date_obj.strftime('%Y-%m-%d')
        except ValueError:
            continue
    print(f"Error converting date: {date_str}")
    return date_str

def clean_time_format(time_str, date_str):
    """Clean the time format and convert it to 'YYYY-MM-DD HH:MM:SS'."""
    try:
        # Remove any non-time characters like '*'
        clean_time_str = ''.join(filter(lambda x: x.isdigit() or x == ':' or x == ' ' or x == 'A' or x == 'M' or x == 'P', time_str))
        time_obj = datetime.strptime(clean_time_str.strip(), '%I:%M %p')
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        combined_datetime = datetime.combine(date_obj, time_obj.time())
        return combined_datetime.strftime('%Y-%m-%d %H:%M:%S')
    except ValueError as e:
        print(f"Error converting time: {e}")
        return time_str

def insert_show_time(cursor, cinema_id, movie_id, show_date, show_time):
    """Insert show time data into the shows_times table."""
    query = """
    INSERT INTO shows_times (movies_id, cinema_id, shows_date, shows_time_slot)
    VALUES (%s, %s, %s, %s)
    """
    cursor.execute(query, (movie_id, cinema_id, show_date, show_time))

def scrape_nueplex(driver, cursor):
    driver.get('https://nueplex.com/')
    time.sleep(5)
    wait = WebDriverWait(driver, 20)
    site_dropdown = Select(wait.until(EC.presence_of_element_located((By.ID, 'branch'))))
    site_ids = [option.get_attribute('value') for option in site_dropdown.options if option.get_attribute('value') != 'All']
    location_map = {'1': 'DHA', '2': 'Askari IV'}
    cinema_id_map = {'1': 3, '2': 4}
    movie_id = 1
    for site_id in site_ids:
        location = location_map.get(site_id, 'Unknown Location')
        cinema_id = cinema_id_map.get(site_id)
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
        default_date = convert_date_to_uniform_format(default_date)  # Convert date to uniform format
        time.sleep(1)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        showings = soup.find_all('div', class_='movie-shedule')
        for showing in showings:
            title_element = showing.find('h4', class_='eq-height')
            time_element = showing.find('span', class_='time')
            if title_element and time_element:
                title_text = title_element.get_text(strip=True)
                time_text = clean_time_format(time_element.get_text(strip=True), default_date)
                print(f"Nueplex data: {location}, Date: {default_date}, Time: {time_text}")
                insert_show_time(cursor, cinema_id, movie_id, default_date, time_text)

def scrape_cinepax(driver, cursor):
    driver.get('https://cinepax.com/')
    time.sleep(5)
    cinema_links = [
        ("AMANAH MALL LAHORE", "https://cinepax.com/Browsing/Cinemas/Details/0000000012", 12),
        ("BOULEVARD MALL HYDERABAD", "https://cinepax.com/Browsing/Cinemas/Details/0000000010", 44),
        ("HOTELONE FAISALABAD", "https://cinepax.com/Browsing/Cinemas/Details/0000000004", 33),
        ("JINNAH PARK RAWALPINDI", "https://cinepax.com/Browsing/Cinemas/Details/0000000003", 23),
        ("KINGS MALL GUJRANWALA", "https://cinepax.com/Browsing/Cinemas/Details/0000000006", 37),
        ("LAKE CITY LAHORE", "https://cinepax.com/Browsing/Cinemas/Details/0000000007", 16),
        ("MALL OF SIALKOT", "https://cinepax.com/Browsing/Cinemas/Details/0000000013", 42),
        ("NAYYAR MALL GUJRAT", "https://cinepax.com/Browsing/Cinemas/Details/0000000009", 44),
        ("OCEAN MALL KARACHI", "https://cinepax.com/Browsing/Cinemas/Details/0000000002", 1),
        ("PACKAGES MALL LAHORE", "https://cinepax.com/Browsing/Cinemas/Details/0000000014", 15),
        ("WORLD TRADE CENTER ISLAMABAD", "https://cinepax.com/Browsing/Cinemas/Details/0000000011", 24)
    ]
    movie_id = 1

    for cinema_name, cinema_url, cinema_id in cinema_links:
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
                    date_text = convert_date_to_uniform_format(date_text)
                    session_times = session_dates[0].find_next('div', class_='session-times')
                    times = session_times.find_all('time')
                    for time_elem in times:
                        time_text = clean_time_format(time_elem.get_text(strip=True), date_text)
                        print(f"Cinepax data: {cinema_name}, Date: {date_text}, Time: {time_text}")
                        insert_show_time(cursor, cinema_id, movie_id, date_text, time_text)
                break  # Only scrape the first date, then move to the next cinema

def scrape_movie_details(driver, movie_link):
    driver.get(movie_link)

    try:
        # Wait for the showtimes container to load
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[class*='show']"))
        )

        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Find possible containers with 'show' in class name
        possible_containers = soup.find_all('div', class_=lambda x: x and 'show' in x.lower())
        print(f"Found {len(possible_containers)} possible containers")

        for container in possible_containers:
            print(f"Inspecting container: {container.prettify()}")
            showtimes_header = container.find('h4')
            if showtimes_header:
                print(f"Found showtimes header: {showtimes_header.get_text(strip=True)}")
                if 'Showtimes' in showtimes_header.get_text():
                    date_text = showtimes_header.get_text(strip=True).split(' at Atrium Cinemas')[0].replace('Showtimes ', '').strip()
                    print(f"Date: {date_text}")

                    # Find all the showtime elements within this container
                    time_elements = container.find_all('a', class_='normalTip exampleTip')
                    print(f"Found {len(time_elements)} time elements")
                    for time_element in time_elements:
                        time_text = time_element.get_text(strip=True)
                        time_text = clean_time_format(time_text, date_text)
                        print(f"mecinemas data: Atrium, Date: {date_text}, Time: {time_text}")
                    return  # Exit after processing the first showtimes container

        print("Error: Could not find the showtimes container.")
    except Exception as e:
        print(f"Error during scraping: {e}")

def scrape_mecinemas(driver):
    # Navigate to the main page
    url = "https://www.mecinemas.com"
    driver.get(url)

    try:
        # Wait for the page to load and select the Karachi location
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "select.select-city"))
        )
        city_dropdown = driver.find_element(By.CSS_SELECTOR, "select.select-city")
        city_dropdown.click()
        karachi_option = driver.find_element(By.CSS_SELECTOR, "option[value='ATR']")
        karachi_option.click()

        # Wait for the page to redirect to the index page
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a[href='movies.php']"))
        )

        # Wait a bit longer to ensure the page has fully loaded
        time.sleep(5)  # Adjust this value as necessary

        # Directly navigate to the movies.php page for Karachi
        movies_url = "https://www.mecinemas.com/movies.php"
        driver.get(movies_url)

        # Wait for the page to load and display the movie links
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='movie_details.php?code=HO00001264']"))
        )

        # Find and click the link for "Na Baligh Afraad"
        movie_link = driver.find_element(By.CSS_SELECTOR, "a[href*='movie_details.php?code=HO00001264']")
        WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href*='movie_details.php?code=HO00001264']")))
        movie_link.click()

        # Scrape the movie details
        scrape_movie_details(driver, driver.current_url)

    except Exception as e:
        print(f"Error during scraping: {e}")
        
def main():
    # Establish MySQL connection
    conn = mysql.connector.connect(
        host="localhost",
        port=3306,
        user="root",
        password="Georgenaylor123@",
        database="cinema"
    )
    cursor = conn.cursor()

    driver = webdriver.Chrome()
    try:
        # Select Karachi by passing its value attribute
        scrape_nueplex(driver,cursor)
        scrape_cinepax(driver,cursor)

        conn.commit()  # Commit the transaction
    finally:
        cursor.close()
        conn.close()
        driver.quit()

if __name__ == "__main__":
    main()

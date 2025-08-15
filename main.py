import requests
import time
import os
import json
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser
import hashlib

class MindatScraper:
    def __init__(self, delay=2):
        self.base_url = "https://www.mindat.org"
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Academic Research Bot - Contact: your-email@domain.com',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })

        # Load and check robots.txt
        self.rp = RobotFileParser()
        self.rp.set_url(f"{self.base_url}/robots.txt")
        self.rp.read()

        self.create_directories()

        self.scraped_data = {}
        self.failed_minerals = []

    def create_directories(self):
        """Create directories for storing images and data"""
        directories = ['images', 'data', 'logs']
        for directory in directories:
            os.makedirs(directory, exist_ok=True)

    def can_fetch(self, url):
        """Check if URL is allowed by robots.txt"""
        return self.rp.can_fetch('*', url)

    def safe_delay(self):
        """Delay between requests"""
        time.sleep(self.delay)

    def search_mineral(self, mineral_name):
        """
        Search for a mineral using mindat's direct mineral pages
        """
        print(f"Searching for: {mineral_name}")

        # Try common mineral page patterns
        possible_urls = [
            f"{self.base_url}/min-{mineral_name.lower().replace(' ', '-')}.html"
            f"{self.base_url}/{mineral_name.lower().replace(' ', '-')}.html"
        ]

        for url in possible_urls:
            if self.can_fetch(url):
                self.safe_delay()
                try:
                    response = self.session.get(url)
                    if response.status_code == 200:
                        return self.parse_mineral_page(response, mineral_name)
                except requests.RequestException as e:
                    print(f"Error accessing {url}: {e}")

        # Try to find the mineral ID first by browsing the alphabetical list
        mineral_id = self.find_mineral_id(mineral_name)
        if mineral_id:
            mineral_url = f"{self.base_url}/min-{mineral_id}.html"
            if self.can_fetch(mineral_url):
                self.safe_delay()
                try:
                    response = self.session.get(mineral_url)
                    if response.status_code == 200:
                        return self.parse_mineral_page(response, mineral_name)
                except requests.RequestException as e:
                    print(f"Error accessing {mineral_url}: {e}")

        print(f"Could not find mineral page for: {mineral_name}")
        return None

    # def browse_by_letter(self, mineral_name):
    #     """Browse minerals by first letter when direct access fails"""
    #     first_letter = mineral_name[0].lower()
    #     browse_url = f"{self.base_url}/minbyletter.php?letter={first_letter}"
    #
    #     if not self.can_fetch(browse_url):
    #         print(f"Cannot access browse page for letter {first_letter}")
    #         return None
    #
    #     self.safe_delay()
    #     try:
    #         response = self.session.get(browse_url)
    #         response.raise_for_status()
    #
    #         soup = BeautifulSoup(response.content, 'html.parser')
    #
    #         # Look for links to the specific mineral
    #         for link in soup.find_all('a', href=True):
    #             if mineral_name.lower() in link.text.lower():
    #                 mineral_url = urljoin(self.base_url, link['href'])
    #                 if self.can_fetch(mineral_url):
    #                     self.safe_delay()
    #                     mineral_response = self.session.get(mineral_url)
    #                     return self.parse_mineral_page(mineral_response, mineral_name)
    #     except requests.RequestException as e:
    #         print(f"Error browsing by letter {first_letter}: {e}")
    #
    #     return None

    def find_mineral_id(self, mineral_name):
        """Find the mineral ID by browsing the alphabetical listing"""
        first_letter = mineral_name[0].upper()
        browse_url = f"{self.base_url}/strunz.php?l={first_letter}"

        if not self.can_fetch(browse_url):
            print(f"Cannot access browse page for letter {first_letter}")
            return None

        self.safe_delay()
        try:
            response = self.session.get(browse_url)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Look for links to the specific mineral
            for link in soup.find_all('a', href=True):
                link_text = link.get_text(strip=True)
                href = link.get('href', '')

                # Check if this link matches our mineral name
                if (mineral_name.lower() == link_text.lower() or
                        mineral_name.lower() in link_text.lower()):

                    # Extract mineral ID from URL like /min-123.html
                    if '/min-' in href and '.html' in href:
                        try:
                            mineral_id = href.split('/min-')[1].split('.html')[0]
                            print(f"Found mineral ID {mineral_id} for {mineral_name}")
                            return mineral_id
                        except (IndexError, ValueError):
                            continue

        except requests.RequestException as e:
            print(f"Error browsing by letter {first_letter}: {e}")

        return None

    def parse_mineral_page(self, response, mineral_name):
        """Parse a mineral page and extract information"""
        soup = BeautifulSoup(response.content, 'html.parser')

        mineral_data = {
            'name': mineral_name,
            'url': response.url,
            'formula': None,
            'crystal_system': None,
            'hardness': None,
            'images': [],
            'description': None
        }

        # Extract mineral formula
        formula_element = soup.find('span', {'class': 'formula'}) or soup.find('td', string='Formula:')
        if formula_element:
            if formula_element.name == 'td':
                formula_element = formula_element.find_next_sibling('td')
            mineral_data['formula'] = formula_element.get_text(strip=True) if formula_element else None

        # Extract description
        desc_element = soup.find('div', {'class': 'description'}) or soup.find('p')
        if desc_element:
            mineral_data['description'] = desc_element.get_text(strip=True)[:500]

        # Extract images
        images = self.extract_images(soup, mineral_name)
        mineral_data['images'] = images

        # Download images
        self.download_images(images, mineral_name)

        return mineral_data

    def extract_images(self, soup, mineral_name):
        """Extract image URLS from the page"""
        images = []

        # Find all image tags
        for img_tag in soup.find_all('img'):
            src = img_tag.get('src')
            if not src:
                continue

            # Convert relative URLs to absolute
            img_url = urljoin(self.base_url, src)

            # Skip prohibited paths
            prohibited_paths = ['/gallery.php', '/gbif_thumbs/', '/newgalleryp.php']
            if any(path in img_url for path in prohibited_paths):
                continue

            # Skip very small images (like UI elements)
            width = img_tag.get('width')
            height = img_tag.get('height')
            if width and height:
                try:
                    if int(width) < 50 or int(height) < 50:
                        continue
                except ValueError:
                    pass

            # Check if we can fetch this image
            if self.can_fetch(img_url):
                images.append({
                    'url': img_url,
                    'alt': img_tag.get('alt', ''),
                    'title': img_tag.get('title', '')
                })

        print(f"Found {len(images)} images for {mineral_name}")
        return images

    def download_images(self, images, mineral_name):
        """Download images to local storage"""
        mineral_dir = os.path.join('images', self.sanitize_filename(mineral_name))
        os.makedirs(mineral_dir, exist_ok=True)

        for i, img_data in enumerate(images):
            img_url = img_data['url']

            self.safe_delay()

            try:
                response = self.session.get(img_url, stream=True)
                response.raise_for_status()

                # Generate filename
                url_hash = hashlib.md5(img_url.encode()).hexdigest()[:8]
                file_extension = self.get_file_extension(img_url, response.headers.get('content-type', ''))
                filename = f"{mineral_name}_{i+1}_{url_hash}{file_extension}"
                filepath = os.path.join(mineral_dir, self.sanitize_filename(filename))

                # Save image
                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)

                print(f"Downloaded: {filename}")

            except requests.RequestException as e:
                print(f"Failed to download image {img_url}: {e}")

    def sanatize_filename(self, filename):
        """Remove invalid characters from filename"""
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        return filename

    def get_file_extension(self, url, content_type):
        """Determine file extension from URL or content type"""

        # Try to get extension from URL
        parsed_url = urlparse(url)
        path = parsed_url.path
        if '.' in path:
            return os.path.splitext(path)[1]

        # Fallback to content type
        content_type_map = {
            'image/jpeg': '.jpg',
            'image/jpg': '.jpg',
            'image/png': '.png',
            'image/gif': '.gif',
            'image/webp': '.webp',
            'image/bmp': '.bmp'
        }
        return content_type_map.get(content_type, '.jpg')

    def scrape_all_minerals(self, minerals_list):
        """Scrape all minerals in the list"""

        total = len(minerals_list)

        for i, mineral in enumerate(minerals_list, 1):
            print(f"\n[{i}/{total}] Processing: {mineral}")

            try:
                result = self.search_mineral(mineral)
                if result:
                    self.scraped_data[mineral] = result
                    print(f"✓ Successfully scraped {mineral}")
                else:
                    self.failed_minerals.append(mineral)
                    print(f"✗ Failed to scrape {mineral}")

                if i % 10 == 0:
                    self.save_progress()

            except Exception as e:
                print(f"✗ Error processing {mineral}: {e}")
                self.failed_minerals.append(mineral)

        self.save_progress()
        self.generate_report()

    def save_progress(self):
        """Save scraped data to JSON file"""
        with open('data/scraped_minerals.json', 'w', encoding='utf-8') as f:
            json.dump(self.scraped_data, f, indent=2, ensure_ascii=False)

        with open('data/failed_minerals.json', 'w', encoding='utf-8') as f:
            json.dump(self.failed_minerals, f, indent=2)

    def generate_report(self):
        """Generate a summary report"""
        total = len(self.scraped_data) + len(self.failed_minerals)
        successful = len(self.scraped_data)
        failed = len(self.failed_minerals)

        report = f"""
            Mindat Scraping Report
            =====================
            Total minerals processed: {total}
            Successfully scraped: {successful}
            Failed: {failed}
            Success rate: {(successful / total) * 100:.1f}%
        
            Failed minerals:
            {chr(10).join(f"- {mineral}" for mineral in self.failed_minerals)}
        """

        with open('logs/scraping_report.txt', 'w') as f:
            f.write(report)

        print(report)

if __name__ == '__main__':

    minerals_and_rocks = ["Ulexite", "Aragonite", "Azurite", "Calcite"]

    # Initialize scraper
    scraper = MindatScraper(delay=2)  # 2-second delay as required by robots.txt

    # Start scraping
    print("Starting Mindat mineral scraping...")
    print(f"Will process {len(minerals_and_rocks)} minerals/rocks")

    scraper.scrape_all_minerals(minerals_and_rocks)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/

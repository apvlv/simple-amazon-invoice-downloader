import asyncio
from playwright.async_api import async_playwright, TimeoutError
from datetime import datetime
import random
import time
import os
from dotenv import load_dotenv
import locale

locale.setlocale(locale.LC_TIME, 'de_DE')

# Read from .env file
load_dotenv()
email = os.getenv('AMAZON_EMAIL')
password = os.getenv('AMAZON_PASSWORD')
download_dir = os.getenv('DOWNLOAD_DIR', './downloads')

def sleep():
    # Add human latency
    # Generate a random sleep time between 2 and 5 seconds
    sleep_time = random.uniform(2, 5)
    time.sleep(sleep_time)

async def main():
    # Parse date ranges into start_date and end_date
    year = str(datetime.now().year)  # current year

    start_date, end_date = year + "0101", year + "1231"
    start_date = datetime.strptime(start_date, "%Y%m%d")
    end_date = datetime.strptime(end_date, "%Y%m%d")

    print(f"Downloading Amazon invoices from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")

    # Ensure the download directory exists
    target_dir = os.path.abspath(download_dir) + "/"
    os.makedirs(target_dir, exist_ok=True)
    print(f"Download directory: {target_dir}")

    # Create Playwright context with Chromium
    pw = await async_playwright().start()
    browser = await pw.chromium.launch(headless=False)
    context = await browser.new_context()
    page = await context.new_page()

    await page.goto("https://www.amazon.de/")

    # Navigate to login
    login_element = await page.wait_for_selector('span >> text=Hallo, anmelden', timeout=0)
    if login_element:
        await login_element.click()

    if email:
        await page.get_by_label("E-Mail-Adresse oder Mobiltelefonnummer").click()
        await page.get_by_label("E-Mail-Adresse oder Mobiltelefonnummer").fill(email)
        await page.get_by_role("button", name="Weiter").click()
        sleep()

    if password:
        await page.get_by_label("Passwort").click()
        await page.get_by_label("Passwort").fill(password)

        # Try to check "Keep me logged in" checkbox - it's optional
        try:
            await page.get_by_label("Angemeldet bleiben").check(timeout=5000)
        except TimeoutError:
            pass

        await page.get_by_role("button", name="Anmelden").click()
        sleep()

    # Navigate to orders page - try different selectors
    try:
        orders_element = await page.wait_for_selector('a >> text=Warenrücksendungen', timeout=10000)
        if orders_element:
            await orders_element.click()
    except TimeoutError:
        try:
            orders_element = await page.wait_for_selector('a >> text=Meine Bestellungen', timeout=10000)
            if orders_element:
                await orders_element.click()
        except TimeoutError:
            try:
                orders_element = await page.wait_for_selector('a[href*="your-orders"]', timeout=10000)
                if orders_element:
                    await orders_element.click()
            except TimeoutError:
                print("Could not find orders page link automatically.")
                print("Please manually navigate to your orders page and then restart the script.")
                return
    sleep()

    # Get a list of years from the select options
    select = await page.query_selector('select#time-filter')
    if not select:
        print("Could not find time filter dropdown")
        return
    years = (await select.inner_text()).split("\n")

    # Filter years to include only numerical years (YYYY)
    years = [year for year in years if year.isnumeric()]

    # Filter years to include only the years between start_date and end_date inclusively
    years = [year for year in years if start_date.year <= int(year) <= end_date.year]
    years.sort(reverse=True)

    print(f"Processing years: {years}")

    # Year Loop (Run backwards through the time range from years to pages to orders)
    invoice_count = 0
    for year in years:
        print(f"\nProcessing year: {year}")

        # Select the year in the order filter
        await page.select_option('form[action="/your-orders/orders"] select#time-filter', value=f"year-{year}")
        sleep()

        # Page Loop
        first_page = True
        done = False
        page_number = 1

        while not done:
            # Go to the next page pagination, and continue downloading
            try:
                if first_page:
                    first_page = False
                else:
                    print("Moving to next page...")
                    await page.click('.a-last a')
                    page_number = page_number + 1
                sleep()
            except TimeoutError:
                print("No more pages.")
                break

            print(f"Analyzing page {page_number}")

            # Use the working selector based on Amazon's current page structure
            order_cards = await page.query_selector_all(".order-card")
            print(f"Found {len(order_cards)} orders on this page")

            for order_card in order_cards:
                # Parse the order card to create the date and file_name
                spans = await order_card.query_selector_all("span")
                if len(spans) < 10:
                    continue

                try:
                    # Find date in spans - it's usually in format "dd. Month YYYY"
                    date_text = None
                    for span in spans[:5]:  # Check first 5 spans for date
                        text = await span.inner_text()
                        if ". " in text and any(month in text for month in ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober", "November", "Dezember"]):
                            date_text = text
                            break

                    if not date_text:
                        continue

                    date = datetime.strptime(date_text, "%d. %B %Y")
                except (ValueError, IndexError):
                    continue

                try:
                    # Find total amount - look for text with € symbol
                    total = "0,00"
                    orderid = "unknown"

                    for span in spans:
                        text = await span.inner_text()
                        if "€" in text and "," in text:
                            total = text.replace("€", "").replace(".", "").strip()
                            break

                    # Find order ID - look for pattern in order links
                    order_links = await order_card.query_selector_all("a")
                    for link in order_links:
                        href = await link.get_attribute("href")
                        if href and "orderID=" in href:
                            orderid = href.split("orderID=")[1].split("&")[0]
                            break

                    date_str = date.strftime("%Y%m%d")
                    file_name = f"{target_dir}{date_str}_{total}_amazon_{orderid}_"

                except Exception:
                    continue

                # Check date range
                if date > end_date:
                    continue
                elif date < start_date:
                    done = True
                    break

                # Look for invoice link
                invoice_popover = await order_card.query_selector('xpath=//a[contains(text(), "Rechnung")]')
                if not invoice_popover:
                    continue

                await invoice_popover.click()
                sleep()

                # Find invoice download links
                invoice_selector = 'xpath=//div[contains(@class, "a-popover-content") and not(contains(@style, "display: none"))]//a[contains(text(), "Rechnung") and not(ancestor::*[contains(@style, "display: none")])]'
                invoices = await page.query_selector_all(invoice_selector)

                # Download all invoices
                for invoice in invoices:
                    href = await invoice.get_attribute("href")
                    if href and ".pdf" in href:
                        invoice_count += 1
                        invoice_number = f'{invoice_count:03}'

                        if not href.startswith("http"):
                            link = "https://www.amazon.de" + href
                        else:
                            link = href

                        print(f"Downloading invoice {invoice_number} for order {orderid} ({date.strftime('%Y-%m-%d')})")

                        try:
                            # Start waiting for the download
                            async with page.expect_download() as download_info:
                                # Perform the action that initiates download
                                await invoice.click(modifiers=["Alt"])
                                sleep()
                            download = await download_info.value

                            # Wait for the download process to complete and save the downloaded file
                            filename = file_name + invoice_number + ".pdf"
                            await download.save_as(filename)
                            print(f"Saved: {os.path.basename(filename)}")
                        except Exception as e:
                            print(f"Error downloading invoice: {e}")

    print(f"\nDownload complete! Downloaded {invoice_count} invoices to {target_dir}")

    # Close the browser
    await context.close()
    await browser.close()
    await pw.stop()

if __name__ == "__main__":
    asyncio.run(main())

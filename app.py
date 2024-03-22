from flask import Flask, render_template, request, send_file
from playwright.sync_api import sync_playwright
import pandas as pd
# import time
import os
import zipfile

app = Flask(__name__)


def main(search_for, total):
    names_list = []
    address_list = []
    website_list = []
    phones_list = []
    reviews_c_list = []
    reviews_a_list = []
    store_s_list = []
    in_store_list = []
    store_del_list = []
    place_t_list = []
    open_list = []
    intro_list = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        page.goto("https://www.google.com/maps/@32.9817464,70.1930781,3.67z", timeout=60000)
        page.wait_for_timeout(100)

        page.locator('//input[@id="searchboxinput"]').fill(search_for)
        page.wait_for_timeout(100)

        page.keyboard.press("Enter")
        page.wait_for_timeout(100)

        page.hover('//a[contains(@href, "https://www.google.com/maps/place")]')

        previously_counted = 0
        while True:
            page.mouse.wheel(0, 10000)
            page.wait_for_timeout(3000)

            if (page.locator('//a[contains(@href, "https://www.google.com/maps/place")]').count() >= total):
                listings = page.locator('//a[contains(@href, "https://www.google.com/maps/place")]').all()[:total]
                listings = [listing.locator("xpath=..") for listing in listings]
                print(f"Total Found: {len(listings)}")
                break
            else:
                if (page.locator(
                        '//a[contains(@href, "https://www.google.com/maps/place")]').count() == previously_counted):
                    listings = page.locator('//a[contains(@href, "https://www.google.com/maps/place")]').all()
                    print(f"Arrived at all available\nTotal Found: {len(listings)}")
                    break
                else:
                    previously_counted = page.locator(
                        '//a[contains(@href, "https://www.google.com/maps/place")]').count()
                    print(f"Currently Found: ",
                          page.locator('//a[contains(@href, "https://www.google.com/maps/place")]').count())

        for listing in listings:
            listing.click()
            page.wait_for_timeout(5000)

            name_xpath = '//div[@class="TIHn2 "]//h1[@class="DUwDvf lfPIob"]'
            address_xpath = '//button[@data-item-id="address"]//div[contains(@class, "fontBodyMedium")]'
            website_xpath = '//a[@data-item-id="authority"]//div[contains(@class, "fontBodyMedium")]'
            phone_number_xpath = '//button[contains(@data-item-id, "phone:tel:")]//div[contains(@class, "fontBodyMedium")]'
            reviews_count_xpath = '//div[@class="TIHn2 "]//div[@class="fontBodyMedium dmRWX"]//div//span//span//span[@aria-label]'
            reviews_average_xpath = '//div[@class="TIHn2 "]//div[@class="fontBodyMedium dmRWX"]//div//span[@aria-hidden]'

            info1 = '//div[@class="LTs0Rc"][1]'
            info2 = '//div[@class="LTs0Rc"][2]'
            info3 = '//div[@class="LTs0Rc"][3]'
            opens_at_xpath = '//button[contains(@data-item-id, "oh")]//div[contains(@class, "fontBodyMedium")]'  # time
            opens_at_xpath2 = '//div[@class="MkV9"]//span[@class="ZDu9vd"]//span[2]'
            place_type_xpath = '//div[@class="LBgpqf"]//button[@class="DkEaL "]'
            intro_xpath = '//div[@class="WeS02d fontBodyMedium"]//div[@class="PYvSYb "]'

            if page.locator(intro_xpath).count() > 0:
                Introduction = page.locator(intro_xpath).inner_text()
                intro_list.append(Introduction)
            else:
                Introduction = ""
                intro_list.append("None Found")

            if page.locator(reviews_count_xpath).count() > 0:
                temp = page.locator(reviews_count_xpath).inner_text()
                temp = temp.replace('(', '').replace(')', '').replace(',', '')
                Reviews_Count = int(temp)
                reviews_c_list.append(Reviews_Count)
            else:
                Reviews_Count = ""
                reviews_c_list.append(Reviews_Count)

            if page.locator(reviews_average_xpath).count() > 0:
                temp = page.locator(reviews_average_xpath).inner_text()
                temp = temp.replace(' ', '')
                Reviews_Average = float(temp)
                reviews_a_list.append(Reviews_Average)
            else:
                Reviews_Average = ""
                reviews_a_list.append(Reviews_Average)

            if page.locator(info1).count() > 0:
                temp = page.locator(info1).inner_text()
                temp = temp.split('·')
                check = temp[1]
                check = check.replace("\n", "")
                if 'shop' in check:
                    Store_Shopping = check
                    store_s_list.append("Yes")
                elif 'pickup' in check:
                    In_Store_Pickup = check
                    in_store_list.append("Yes")
                elif 'delivery' in check:
                    Store_Delivery = check
                    store_del_list.append("Yes")
            else:
                Store_Shopping = ""
                store_s_list.append("No")

            if page.locator(info2).count() > 0:
                temp = page.locator(info2).inner_text()
                temp = temp.split('·')
                check = temp[1]
                check = check.replace("\n", "")
                if 'pickup' in check:
                    In_Store_Pickup = check
                    in_store_list.append("Yes")
                elif 'shop' in check:
                    Store_Shopping = check
                    store_s_list.append("Yes")
                elif 'delivery' in check:
                    Store_Delivery = check
                    store_del_list.append("Yes")
            else:
                In_Store_Pickup = ""
                in_store_list.append("No")

            if page.locator(info3).count() > 0:
                temp = page.locator(info3).inner_text()
                temp = temp.split('·')
                check = temp[1]

                check = check.replace("\n", "")
                if 'Delivery' in check:
                    Store_Delivery = check
                    store_del_list.append("Yes")
                elif 'pickup' in check:
                    In_Store_Pickup = check
                    in_store_list.append("Yes")
                elif 'shop' in check:
                    Store_Shopping = check
                    store_s_list.append("Yes")
            else:
                # l1.append("")
                Store_Delivery = ""
                store_del_list.append("No")

            if page.locator(opens_at_xpath).count() > 0:
                opens = page.locator(opens_at_xpath).inner_text()

                opens = opens.split('⋅')

                if len(opens) != 1:
                    opens = opens[1]

                else:
                    opens = page.locator(opens_at_xpath).inner_text()
                    # print(opens)
                opens = opens.replace("\u202f", "")
                Opens_At = opens
                open_list.append(Opens_At)

            else:
                Opens_At = ""
                open_list.append(Opens_At)
            if page.locator(opens_at_xpath2).count() > 0:
                opens = page.locator(opens_at_xpath2).inner_text()

                opens = opens.split('⋅')
                opens = opens[1]
                opens = opens.replace("\u202f", "")
                Opens_At = opens
                open_list.append(Opens_At)

            if page.locator(name_xpath).count() > 0:
                Name = page.locator(name_xpath).inner_text()
                names_list.append(Name)
            else:
                Name = ""
                names_list.append(Name)
            if page.locator(address_xpath).count() > 0:
                Address = page.locator(address_xpath).inner_text()
                address_list.append(Address)
            else:
                Address = ""
                address_list.append(Address)
            if page.locator(website_xpath).count() > 0:
                Website = page.locator(website_xpath).inner_text()
                website_list.append(Website)
            else:
                Website = ""
                website_list.append(Website)
            if page.locator(phone_number_xpath).count() > 0:
                Phone_Number = page.locator(phone_number_xpath).inner_text()
                phones_list.append(Phone_Number)
            else:
                Phone_Number = ""
                phones_list.append(Phone_Number)
            if page.locator(place_type_xpath).count() > 0:
                Place_Type = page.locator(place_type_xpath).inner_text()
                place_t_list.append(Place_Type)
            else:
                Place_Type = ""
                place_t_list.append(Place_Type)

        df = pd.DataFrame(list(
            zip(names_list, website_list, intro_list, phones_list, address_list, reviews_c_list, reviews_a_list,
                store_s_list, in_store_list, store_del_list, place_t_list, open_list)),
            columns=['Names', 'Website', 'Introduction', 'Phone Number', 'Address', 'Review Count',
                     'Average Review Count', 'Store Shopping', 'In Store Pickup', 'Delivery', 'Type', 'Opens At'])

        for column in df.columns:
            if df[column].nunique() == 1:
                df.drop(column, axis=1, inplace=True)

        browser.close()
        return df


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/scrape', methods=['POST'])
def scrape():
    search_query = request.form['search_query']
    total_results = int(request.form['total'])

    df = main(search_query, total_results)

    # Create a temporary directory to store the CSV file
    temp_dir = 'temp_csv'
    os.makedirs(temp_dir, exist_ok=True)

    # Save the DataFrame to a CSV file
    csv_path = os.path.join(temp_dir, 'data.csv')
    df.to_csv(csv_path, index=False)

    # Create a zip file
    zip_path = os.path.join(temp_dir, 'data.zip')
    with zipfile.ZipFile(zip_path, 'w') as zip_file:
        zip_file.write(csv_path, 'data.csv')

    os.remove(csv_path)

    return send_file(zip_path, as_attachment=True, download_name='data.zip', mimetype='application/zip')


@app.route('/download_zip')
def download_zip():
    zip_path = 'temp_csv/data.zip'
    return send_file(zip_path, as_attachment=True, download_name='data.zip', mimetype='application/zip')


if __name__ == '__main__':
    app.run(debug=True)

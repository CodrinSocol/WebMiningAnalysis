import pandas as pd
from bs4 import BeautifulSoup
import requests
from pandas import DataFrame


# Master function that scrapes the entire dataset passed as param
def scrape_not_recomended_reviews(df_restaurants: DataFrame):
    df_reviews = pd.DataFrame(columns=[
        'restaurant_name',
        'restaurant_url',
        'review_url_location',
        'review_page_number',
        'star_rating',
        'review_lang',
        'review_date',
        'review_text',
        'word_count',
        'char_count',
        'reviewer_name',
        'reviewer_location',
        'reviewer_friend_count',
        'reviewer_review_count',
        'reviewer_photo_count',
        'reviewer_has_profile_image',
    ])

    # iterate through each restaurant
    for (idx, row) in df_restaurants.iterrows():
        url = row['not_recommended_url']
        raw_url = url.replace('?not_recommended_start=0', '')
        scrapped_reviews_count = 0
        print(url)

        # get the html content of first page
        response = requests.get(url)
        if response.ok is False:
            print(f'Failed to fetch {url}')
        html = response.content
        print(html)
        soup = BeautifulSoup(html, 'html.parser')

        h3_text = soup.find(class_=['review-list-wide']).find('h3').text
        review_count = int(h3_text.split()[0])

        if review_count == 0:
            continue

        num_pages = review_count // 10 + 1

        for curr_page_idx in range(0, num_pages):
            curr_page_url = f'{raw_url}?not_recommended_start={curr_page_idx * 10}'
            print(curr_page_url)

            response = requests.get(curr_page_url)
            if response.ok is False:
                print(f'Failed to fetch {curr_page_url}')
                continue
            html = response.content
            soup = BeautifulSoup(html, 'html.parser')
            list_of_ratings = [float(x.get("title").split()[0]) for x in soup.select('.review-list-wide .rating-large')]

            raw_reviews = soup.select('.review-list-wide p')
            list_of_reviews = [x.text for x in raw_reviews]

            word_counts = [len(x.split()) for x in list_of_reviews]
            char_counts = [len(x) for x in list_of_reviews]

            review_langs = [x.get("lang") for x in raw_reviews]
            review_dates = [x.text.strip() for x in soup.select('.review-list-wide .rating-qualifier')]

            reviewer_names = [x.text for x in soup.select('.review-list-wide .user-display-name')]
            reviewer_locations = [x.text for x in soup.select('.review-list-wide .responsive-hidden-small b')]

            reviewer_friend_counts = [x.text.strip().split()[0] for x in soup.select('.review-list-wide .friend-count')]
            reviewer_review_counts = [x.text.strip().split()[0] for x in soup.select('.review-list-wide .review-count')]

            profile_images = [1 if "default_avatar" not in x.get('src') else 0 for x in soup.select('.review-list-wide .pb-60s .photo-box-img')]

            reviewer_photo_counts = []
            review_containers = soup.select('.review-list-wide .review')

            # Photo counter could be missing, so we need to search if it exists in the entire review container.
            for container in review_containers:
                photo_count_tag = container.select_one('.photo-count')

                if photo_count_tag is not None:
                    reviewer_photo_counts.append(photo_count_tag.text.strip().split()[0])
                else:
                    reviewer_photo_counts.append('0')

            # Iterate through the page and add reviews to the final DataFrame.
            for i in range(0, len(list_of_reviews)):
                scrapped_reviews_count += 1

                df_reviews = df_reviews._append({
                    'restaurant_name': row['name'],
                    'restaurant_url': row['url'],
                    'review_url_location': url,
                    'review_page_number': curr_page_idx + 1,
                    'star_rating': list_of_ratings[i],
                    'review_lang': review_langs[i],
                    'review_date': review_dates[i],
                    'review_text': list_of_reviews[i],
                    'word_count': word_counts[i],
                    'char_count': char_counts[i],
                    'reviewer_name': reviewer_names[i],
                    'reviewer_location': reviewer_locations[i],
                    'reviewer_friend_count': reviewer_friend_counts[i],
                    'reviewer_review_count': reviewer_review_counts[i],
                    'reviewer_photo_count': reviewer_photo_counts[i],
                    'reviewer_has_profile_image': profile_images[i],
                }, ignore_index=True)

        print(f'Successfully scrapped {scrapped_reviews_count} out of {review_count} reviews for {row["name"]}')
        # break

            # # write df to file
    df_reviews.to_csv('D:/Repositories/WebMiningAnalysis/assignment_1/data/scrapped_reviews.csv', index=False)
            # break

            # iterate through all the other pages (if they exist)




            # # save the html content to a file
            # with open(f'D:/Repositories/WebMiningAnalysis/assignment_1/try.html', 'wb') as f:
            #     f.write(html)










# ################
# # STEP 1: Motherlist (condensed)
#
#
# # data import
#
#
# # Add a new column 'not_recommended_link' based on the existing 'url' column
#
#
# # ###############STEP 2: Going through the subpages
#
# # collect variables for restaurants
# url = df_restaurants['not_recommended_url'][2]
# name_business = df_restaurants['name'][2]
#
# html = requests.get(url)
# soup = BeautifulSoup(html.content, 'lxml')
#
# #soup_username = soup.select()
# soup_username = soup.select('')
# soup_username[1:5]
#
# username = []
#
# for name in soup_username:
#     username.append(name.string)
#
# username[0:5]
#
# # Get ratings
# soup_stars=soup.select('')
# soup_stars[0:5]
#
# rating = []
#
# for stars in soup_stars:
#     rating.append(stars.attrs['title'])
#
# rating[0:5]
#
# # Get rid of text "star rating"
# import re
# rating  = [re.sub(' star rating', '',  r) for r in rating]
#
# #convert from string to number
# rating = [float(i) for i in rating]
#
# #Get date of rating
# soup_date=soup.select('')
# soup_date[0:5]
#
# date_review = []
#
# for date in soup_date:
#     date_review.append(date.text.strip())
#
# date_review[0:5]
#
# # Get rid of text "Updated review", "Previous review", "\n", and multiple spaces
# date_review  = [re.sub('Updated review', '',  dr) for dr in date_review]
# date_review  = [re.sub('Previous review', '',  dr) for dr in date_review]
# date_review  = [re.sub('\n', '',  dr) for dr in date_review]
# date_review  = [re.sub(' ', '',  dr) for dr in date_review]
#
# #Get the review text
# html_texts=soup.select('')
# html_texts[0:10]
#
# html_text = []
#
# for t in html_texts:
#     html_text.append(t.get_text())
#
# html_text
#
# # Remove certain characters
# html_text  = [re.sub('\xa0', '',  ht) for ht in html_text]
#
# ##Combine everything to dataset
# #add name business
# name_business_mult = [name_business] * len(username)
# url_restaurant_mult = [url] * len(username)
#
# RatingDataSet = list(zip(name_business_mult, url_restaurant_mult, username, rating, date_review, html_text))
#
# df_rating = pd.DataFrame(data = RatingDataSet, columns=['name_business','url', 'username', 'rating', 'date_review', 'text'])
# df_rating.iloc[:10]
#
# df_rating.to_csv('..../boston_ratings_workshop.csv',index=False,header=True,encoding='utf8')
#
# #####Step 3: Putting Step 2 in a loop
#
# for u in range(0,4):
#     try:
#         #collect variables for restaurants
#         url = df_restaurants['not_recommended_url'][u]
#         name_business = df_restaurants['name'][u]
#
#         html = requests.get(url)
#         soup = BeautifulSoup(html.content, 'lxml')
#
#         soup_username = soup.select('')
#         soup_username[1:5]
#
#         username = []
#
#         for name in soup_username:
#             username.append(name.string)
#
#         username[0:5]
#
#         # Get ratings
#         soup_stars=soup.select('')
#         soup_stars[0:5]
#
#         rating = []
#
#         for stars in soup_stars:
#             rating.append(stars.attrs['title'])
#
#         rating[0:5]
#
#         # Get rid of text "star rating"
#         import re
#         rating  = [re.sub(' star rating', '',  r) for r in rating]
#
#         #convert from string to number
#         rating = [float(i) for i in rating]
#
#         #Get date of rating
#         soup_date=soup.select('')
#         soup_date[0:5]
#
#         date_review = []
#
#         for date in soup_date:
#             date_review.append(date.text.strip())
#
#         date_review[0:5]
#
#         # Get rid of text "Updated review", "Previous review", "\n", and multiple spaces
#         date_review  = [re.sub('Updated review', '',  dr) for dr in date_review]
#         date_review  = [re.sub('Previous review', '',  dr) for dr in date_review]
#         date_review  = [re.sub('\n', '',  dr) for dr in date_review]
#         date_review  = [re.sub(' ', '',  dr) for dr in date_review]
#
#         #Get the review text
#         html_texts=soup.select('')
#         html_texts[0:10]
#
#         html_text = []
#
#         for t in html_texts:
#             html_text.append(t.get_text())
#
#         html_text
#
#         # Remove certain characters
#         html_text  = [re.sub('\xa0', '',  ht) for ht in html_text]
#
#
#         name_business_mult = [name_business] * len(username)
#         url_restaurant_mult = [url] * len(username)
#
#         RatingDataSet = list(zip(name_business_mult, url_restaurant_mult, username, rating, date_review, html_text))
#
#         df_rating = pd.DataFrame(data = RatingDataSet, columns=['name_business', 'url', 'username', 'rating', 'date_review', 'text'])
#
#         with open('..../boston_ratings150_workshop.csv', 'a',newline='') as f:
#             df_rating.to_csv(f, index=False, header=False, encoding='utf8')
#
#         print(u)
#         import time
#         time.sleep(2)
#
#     except:
#         print("A page was not loaded correctly")


def main():
    df_restaurants = pd.read_csv('D:/Repositories/WebMiningAnalysis/assignment_1/data/group_10_milwaukee.csv')
    df_restaurants['not_recommended_url'] = df_restaurants['url'].apply(
        lambda x: x.replace('/biz/', '/not_recommended_reviews/') + '?not_recommended_start=0' if '/biz/' in x else x)

    scrape_not_recomended_reviews(df_restaurants)

if __name__ == "__main__":
    main()
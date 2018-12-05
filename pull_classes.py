'''
Pull data from two APIs: iDreamBooks, and
Google Books.

Checkbahng:
1) recommends five books per genre with price and description
2) identifies critic review, and author review
3) shows purchase price and purchase links for a book
4) recommends a minimally related book the user looked
   up the purchase information for.
'''
from secret import iDreamBooksKey
import requests
import statistics

class genre_recommend():
  iDreamBooks_recommend_base_url='http://idreambooks.com/api/publications/'\
  'recent_recos.json?key={key}&slug={genre}'
  google_base_url='https://www.googleapis.com/books/v1/volumes?q={title}'

  def __init__(self,genre='all-books'):
    self.genre=genre

  def get_iDB_url(self):
    return self.iDreamBooks_recommend_base_url.format(key=iDreamBooksKey,
      genre=self.genre)

  def pull_recommend_url(self):
    iDB_recommend_url=self.get_iDB_url()
    return requests.get(iDB_recommend_url).json()

  '''
    pull top five title and author pairs from iDreamBooks
    initiailze as list of dictionaries with the below key, value pairing:
     'title':title
     'author':author
  '''

  def trim_iDB_recommend(self):
    iDB_recommendation_dict=self.pull_recommend_url()
    main_recommendation_list=[]
    for index in range(min(5,len(iDB_recommendation_dict))):
      recommend_book_dict={}
      recommend_book_dict['title']=iDB_recommendation_dict[index]['title']
      recommend_book_dict['author']=iDB_recommendation_dict[index]['author']
      main_recommendation_list.append(recommend_book_dict)
    return main_recommendation_list

  def get_google_url(self,title):
    return self.google_base_url.format(title=title)

  def pull_google_url(self,title):
    google_sub_url=self.get_google_url(title)
    return requests.get(google_sub_url).json()

  '''
  Loop through the iDB list of dictionaries and pull
  the top three Google API pull result for each title.

  Assemble the google pull into a list of dictionaties
  with the below key, value pair:
    'title':title
    'author':list of authors
    'price':price
    'description':book description

  Each individual Google dictionary's index will match the corresponding
  iDB dictionary's index.
  '''
  def pull_related_google_data(self):
    main_recommendation_list=self.trim_iDB_recommend()
    sub_google_list=[]
    for index in range(len(main_recommendation_list)):
      title=main_recommendation_list[index]['title'].replace(" ","+")
      google_dict=self.pull_google_url(title)['items']
      sub_sub_google_list=[]
      for item in range(min(len(google_dict),3)):
        volumeInfo=google_dict[item]['volumeInfo']
        saleInfo=google_dict[item]['saleInfo']
        assembled_google_dict={}
        assembled_google_dict['title']=volumeInfo.get('title','No title')
        assembled_google_dict['author']=volumeInfo.get('authors',['No author'])
        assembled_google_dict['description']=volumeInfo.get('description',
          'No description')
        assembled_google_dict['price']=saleInfo.get('retailPrice',
          {'amount':'Not for sale'}).get('amount')
        sub_sub_google_list.append(assembled_google_dict)
      sub_google_list.append(sub_sub_google_list)
    return sub_google_list

  '''
  For each title/author dictionary in iDreamBooks,
  Loop through a google pull dictionary with a corresponding index.
  if the title matches,
  and if the iDreamBooks author is included in Google books list of authors
  update the corresponding iDreamBooks dictionary with
  'price': price - default: not for sale
  'description': book description
  '''
  def match_recommendations(self):
    main_recommendation_list=self.trim_iDB_recommend()
    sub_google_list=self.pull_related_google_data()
    for index in range(len(sub_google_list)):
      for pull in range(len(sub_google_list[index])):
        if main_recommendation_list[index]['title'].split(":")[0]\
        ==sub_google_list[index][pull]['title']\
        and\
        main_recommendation_list[index]['author'] in\
        sub_google_list[index][pull]['author']:
          main_recommendation_list[index]['description']\
          =sub_google_list[index][pull]['description']
          if sub_google_list[index][pull]['price'] != 'Not for sale':
            main_recommendation_list[index]['price']\
            =sub_google_list[index][pull]['price']
            break
          else:
           main_recommendation_list[index]['price']='Not for sale'
        else:
          main_recommendation_list[index]['description']='Not available'
          main_recommendation_list[index]['price']='Not for sale'
    return main_recommendation_list

class pull_review():
  review_base_url='http://idreambooks.com/api/books/reviews.json?q={title}'\
  '&key={key}'
  google_base_url='https://www.googleapis.com/books/v1/volumes?q={title}'

  def __init__(self,title):
    self.title=title

  def get_review_url(self):
    query_title=self.title.replace("%20","-")
    return self.review_base_url.format(title=query_title,key=iDreamBooksKey)

  def pull_review_url(self):
    review_url=self.get_review_url()
    return requests.get(review_url).json()

  '''
  pull the critic review from iDreamBooks based on title.
  Each pull will return a list of dictionaries of critic reviews.
  Pull out the critic score out of each dictionary within the list, and
  add to a central score list. Find the mean of the scores.
  This will result in one dictionary with
  'title':title
  'author':author
  'critic_review': mean critic score
  '''
  def trim_iDB_review_pull(self):
    untrimmed_dict=self.pull_review_url()['book']
    review_dict={}
    review_dict['title']=untrimmed_dict.get('title','No matching book')
    review_dict['author']=untrimmed_dict.get('author','No matching book')
    critic_reviews=untrimmed_dict.get('critic_reviews','No critic review')
    if critic_reviews != 'No critic review':
      critic_scores=[]
      try:
        for review in range(len(critic_reviews)):
          critic_scores.append(critic_reviews[review].get('star_rating','Not reviewed'))
        mean_critic_score=round(statistics.mean(critic_scores),2)
        review_dict['critic_review']=mean_critic_score
      except statistics.StatisticsError as e:
        review_dict['critic_review']='No critic reviews'
    else:
      review_dict['critic_review']='No critic reviews'
    return review_dict

  def get_google_url(self,title):
    return self.google_base_url.format(title=title)

  def pull_google_url(self,title):
    google_sub_url=self.get_google_url(title)
    return requests.get(google_sub_url).json()

  '''
  search the same title to pull top three Google API result for each title
  and assemble into a list of dictionaries. Trim the pull to get only the reviews,
  title, and author. Each dictionary will have
  'title':title
  'author':list of authors
  'reader_review': average review
  '''
  def pull_related_google_data(self):
    main_review_dict=self.trim_iDB_review_pull()
    sub_google_list=[]
    title=main_review_dict['title'].replace(" ","+")
    google_dict=self.pull_google_url(title)['items']
    for item in range(min(len(google_dict),3)):
      volumeInfo=google_dict[item]['volumeInfo']
      assembled_google_dict={}
      assembled_google_dict['title']=volumeInfo.get('title','No title')
      assembled_google_dict['author']=volumeInfo.get('authors',['No author'])
      assembled_google_dict['reader_review']=volumeInfo.get('averageRating',
        'No reader reviews')
      sub_google_list.append(assembled_google_dict)
    return sub_google_list

  '''
  Loop through each google dictionary in the list.
  if the title matches,
  and if the iDreamBooks author is included in Google books list of authors
  update the iDreamBooks review dictionary with:
  'reader_review': average google review
  '''
  def match_reviews(self):
    main_review_dict=self.trim_iDB_review_pull()
    sub_google_list=self.pull_related_google_data()
    for index in range(len(sub_google_list)):
      if sub_google_list[index]['title']==main_review_dict['title']\
      and main_review_dict['author'] in sub_google_list[index]['author']:
        main_review_dict['reader_review']=sub_google_list[index]['reader_review']
        break
      else:
        main_review_dict['reader_review']='Not available'
    return main_review_dict

class purchase_info():
  review_base_url='http://idreambooks.com/api/books/reviews.json?q={title}'\
  '&key={key}'
  google_base_url='https://www.googleapis.com/books/v1/volumes?q={title}'


  def __init__(self,title):
    self.title=title

  def get_review_url(self):
    query_title=self.title.replace("%20","-")
    return self.review_base_url.format(title=query_title,key=iDreamBooksKey)

  def pull_review_url(self):
    review_url=self.get_review_url()
    return requests.get(review_url).json()

  '''
  pull only the title and author from iDreamBooks review pull. This will result in
  one dictionary with
  'title': title
  'author': author
  '''
  def trim_iDB_purchase_pull(self):
    untrimmed_dict=self.pull_review_url()['book']
    purchase_dict={}
    purchase_dict['title']=untrimmed_dict.get('title','No matching book')
    purchase_dict['author']=untrimmed_dict.get('author','No matching book')
    return purchase_dict

  def get_google_url(self,title):
    return self.google_base_url.format(title=title)

  def pull_google_url(self,title):
    google_sub_url=self.get_google_url(title)
    return requests.get(google_sub_url).json()

  '''
  search the same title and pull the top three google api result for each title.
  assemble into a list of dictionaries, pull only the retail price and buyLink
  'title': title
  'author':list of authors
  'price':saleInfo['retailPrice']['amount']
  'purchase-link':saleInfo['buyLink']
  '''

  def pull_related_google_data(self):
    main_purchase_dict=self.trim_iDB_purchase_pull()
    sub_google_list=[]
    title=main_purchase_dict['title'].replace(" ","+")
    google_dict=self.pull_google_url(title)['items']
    for item in range(min(len(google_dict),3)):
      volumeInfo=google_dict[item]['volumeInfo']
      saleInfo=google_dict[item]['saleInfo']
      assembled_google_dict={}
      assembled_google_dict['title']=volumeInfo.get('title','No title')
      assembled_google_dict['author']=volumeInfo.get('authors',['No author'])
      assembled_google_dict['price']=saleInfo.get('retailPrice',
          {'amount':'Not for sale'}).get('amount')
      assembled_google_dict['purchase-link']=saleInfo.get('buyLink','Not for sale')
      sub_google_list.append(assembled_google_dict)
    return sub_google_list

  '''
  Loop through each google dictionary in the list.
  if the title matches,
  and if the iDreamBooks author is included in Google books list of authors
  update the iDreamBooks review dictionary with:
  'price': price
  'purchase-link': Google Play buy link
  '''
  def match_purchase_info(self):
    main_purchase_list=self.trim_iDB_purchase_pull()
    sub_google_list=self.pull_related_google_data()
    for index in range(len(sub_google_list)):
      if sub_google_list[index]['title']==main_purchase_list['title']\
      and main_purchase_list['author'] in sub_google_list[index]['author']:
        main_purchase_list['price']=sub_google_list[index]['price']
        main_purchase_list['purchase-link']=sub_google_list[index]['purchase-link']
        break
      else:
        main_purchase_list['price']='Not for sale'
        main_purchase_list['purchase-link']='Not for sale'
    return main_purchase_list

  '''
  Return the last item from the google API pull as a wild-card item, pull title,
  description, and author.

  This should be the least relevant Google search result
  '''
  def wild_card(self):
    main_purchase_dict=self.trim_iDB_purchase_pull()
    title=main_purchase_dict['title'].replace(" ","+")
    sub_google_list=self.pull_google_url(title)['items']
    wild_list=sub_google_list[-1]
    wild_dict={}
    wild_volume=wild_list['volumeInfo']
    wild_dict['title']=wild_volume.get('title','No recommendation')
    wild_dict['author']=wild_volume.get('authors','Not available')
    wild_dict['description']=wild_volume.get('description','Not available')
    return wild_dict

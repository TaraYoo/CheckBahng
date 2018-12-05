# CheckBahng

CheckBahng recommends books based on genre with its price and description. 
It will also recommend a book that's tangentially related to a book you decide to purchase. 
You can pull the book's critic reviews, and reader reviews, as well as its price, and purchase link by title.

Book title, author, and critic reviews are from iDreamBooks' API.
Book description, price, purchase link, and reader reviews are from Google Books API.

CheckBahng uses Bootstrap's starter template CSS, the table layout from iDreamBook's documentation, and BookBub's Free e-book page layout.

You will need Python 3.6 or above, and Flask to run this app.

# Installation

1. Get the iDreambooks API key from https://idreambooks.com/api. The key form is at the bottom of the page.
2. Save your key in secret.py. Your secret.py file should look like the below:
  iDreamBooksKey = {your key here}
   Save in the same file route as CheckBahng.py and pull_classes.py
3. Pip install Flask
  * If you're using windows, type py -m pip install flask on your command line.
4. To run CheckBahng, go to CheckBahng's folder location in your command line and type py CheckBahng.py

# Endpoints

There are four endpoints.
1. /recommend 

  Lists iDreamBook's 40 valid genres. Click on a genre to see the top five iDreamBooks recommendation for that genre.
  You can also type the genre in yourself - if you choose an option that's not listed, you'll automatically default to all-books.
  
2. /recommend/<genre>

  CheckBahng will return the title, author, price, and description of iDreamBook's top five genre recommendation. Price and description are from the Google Book API. You can click on the title to see a review of the book.
  If there is no match with Google, you'll only get the title and author. Price and description will return as 'Not for sale' and 'Not available' respectively.
  
  This page's layout mimics Bookbub's free e-book page. (https://www.bookbub.com/ebook-deals/free-ebooks) 
  
3. /review/<title>
  
  CheckBahng will return a list of the title, author, critic review, and reader review. 
  The reader reviews are based on Google's reader review. You can click on the title to go to the purchase page.
  
4. /purchase/<title>

  CheckBahng will return a title's price, and purchase link. 
  If you look for a title that doesn't exist in iDreamBook's data base, this endpoint will return a default page that looks like the below:
  title - no matching book
  price - not for sale
  purchase link - not for sale
  
  CheckBahng's price and purchase link information are from Google Books API, which only pulls from the Google Play Store. If the book is not for sale on Google Play, the price will show as 'Not for Sale'.
  
  CheckBahng will also return a wild-card recommendation, which is the least relevant book from the Google API pull for the title you searched for. You will see the title, author, and description of the book
  

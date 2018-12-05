from flask import Flask, render_template, jsonify
from pull_classes import genre_recommend, pull_review, purchase_info

app=Flask(__name__)

@app.route('/recommend')
def list_genres():
  return render_template('genre_listing.html')

@app.route('/recommend/<genre>',methods=['GET'])
def recommend(genre):
  genre_pull=genre_recommend(genre)
  return render_template('recommendation_listing.html',
    recommendations=genre_pull.match_recommendations())

@app.route('/review/<title>',methods=['GET'])
def review(title):
  title_review=pull_review(title)
  return render_template('review_listing.html',
    title=title,
    review_dict=title_review.match_reviews())

@app.route('/purchase/<title>',methods=['GET'])
def purchase(title):
  title_purchase=purchase_info(title)
  return render_template('purchase_listing.html',
    title=title,
    purchase_dict=title_purchase.match_purchase_info(),
    wild=title_purchase.wild_card())

if __name__=='__main__':
  app.run(debug=True)

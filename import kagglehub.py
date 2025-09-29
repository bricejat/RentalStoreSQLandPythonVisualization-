import kagglehub

# Download latest version
path = kagglehub.dataset_download("atanaskanev/sqlite-sakila-sample-database")

print("Path to dataset files:", path)

import numpy as np #linear algebra
import pandas as pd #prodcessing
import kagglehub
from pathlib import Path
import numpy as np  # linear algebra
import pandas as pd  # processing
import sqlite3  # sql
import matplotlib.pyplot as plt  # visual
import seaborn as sns  # visual


# Try to download latest version (optional) — if that works we may get a path
# otherwise fall back to the local copy in dataset/sqlite-sakila-db.
path = None
try:
    path = kagglehub.dataset_download("atanaskanev/sqlite-sakila-sample-database")
    print("kagglehub dataset_download returned:", path)
except Exception as e:
    print("kagglehub.dataset_download failed (continuing):", e)


# Candidate paths (first existing one will be used)
candidates = []
if path:
    candidates.append(Path(path) / "sqlite-sakila.db")
candidates.append(Path("dataset/sqlite-sakila-db/sqlite-sakila.db"))
candidates.append(Path("dataset/sqlite-sakila.db"))
candidates.append(Path("database/sqlite-sakila.db"))
candidates.append(Path("database/sqlite-sakila-db/sqlite-sakila.db"))

db_path = None
for p in candidates:
    if p.exists():
        db_path = p
        break

if db_path is None:
    raise FileNotFoundError(f"Could not find sqlite-sakila.db. Checked: {candidates}")

print("Using database file:", db_path.resolve())

con = sqlite3.connect(str(db_path.resolve()))

# Pulls data from the database and creates a table.
q1 = pd.read_sql('''SELECT *
                    FROM sqlite_master
                    WHERE type = 'table';''', con)
print(q1)

# Table of actors
actors = pd.read_sql('''SELECT *
                        FROM actor
                        ''', con)
print(actors.head())

## Table of payments
payment = pd.read_sql('''SELECT *
                        FROM payment
                        ''', con)
print(payment.head())

## Table of languages
language = pd.read_sql('''SELECT *
                        FROM language;''', con)
print(language.head())

## Table of rentals
rental = pd.read_sql('''SELECT *
                        FROM rental;''', con)
print(rental.head())

## Table of inventory
inventory = pd.read_sql('''SELECT *
                        FROM inventory''', con)
print(inventory.head())

## Table of films
film = pd.read_sql(''' SELECT *
                    FROM film;''', con)
print(film.head())

## ANALYSIS SECTION
year = pd.read_sql('''SELECT release_year as year_released, count(*) as 'Number of filming per year'
                    FROM film
                    GROUP BY year_released;''', con)
print(year.head())

film_rating = pd.read_sql('''SELECT rating, COUNT(*) AS quantity
                                    FROM film
                                    GROUP BY rating
                                    ORDER BY quantity DESC;''', con)
print(film_rating)
## VISUALIZATIONS SECTION

Media = film_rating['quantity'].mean()
plt.figure(figsize=(8,5))
sns.barplot(data=film_rating, x='rating', y='quantity', palette='viridis')
plt.axhline(y=Media, color='b', linestyle='--', label='Media')
plt.text(3, Media + 10, f'Media: {Media:.2f}', ha='left')

plt.title('Number of films per rating')
plt.xlabel('Rating')
plt.ylabel('Quantity')

## VISUALIZATION OF HOW LONG A FILM IS

plt.figure(figsize=(8,2))
plt.boxplot(film['length'].dropna(), vert=False)
plt.title('Distribution of film lengths')
plt.xlabel('Length')
plt.yticks([])
plt.show()

## Creating a new dataframe with an added column to categorize the rental_rate into three sections (High, Medium and Low).
film1 = pd.read_sql('''
    SELECT f.*, c.name AS category,
        CASE
            WHEN f.rental_rate >= 4.0 THEN 'High'
            WHEN f.rental_rate >= 2.0 THEN 'Medium'
            ELSE 'Low'
        END AS rental_rate_category
    FROM film f
    JOIN film_category fc ON f.film_id = fc.film_id
    JOIN category c ON fc.category_id = c.category_id;
''', con)
print(film1.head())

## Quantity by Category
category_counts = (
    film1['category']
    .value_counts()
    .rename_axis('category')
    .reset_index(name='count')
)
print(category_counts)

## Visualization
media1 = category_counts['count'].mean()
print(media1)

plt.figure(figsize=(5,4))
sns.barplot(data=category_counts, x='category', y='count', palette='mako')
plt.axhline(y=media1, color='r', linestyle='--', label='media1')
plt.text(0.5, media1 + 7.5, f'Media: {media1:.2f}', ha='center', va='bottom')
plt.title('Quantity by income ratio per Category')
plt.xlabel('Category')
plt.ylabel('Quantity')
plt.show()

## Movies and their respective original languages
language = pd.read_sql(''' SELECT film.title as Movie_Title, language.name as Language
                        FROM film
                        JOIN language ON film.language_id = language.language_id;''', con)
print(language.head())

# Quantity of movies by language
langauge1 = pd.read_sql(''' SELECT language.name as Language, COUNT(*) as Quantity
                        FROM film
                        JOIN language ON film.language_id = language.language_id
                        GROUP BY language.name;''', con)
print(langauge1)

## Client Table
customer = pd.read_sql(''' SELECT *
                        FROM customer;''', con)
print(customer)

## Top 10 clients

top10_customers = pd.read_sql(''' SELECT c.first_name || ' ' || c.last_name as name_complete,
                                    SUM(p.amount) as Total_spent
                                    FROM customer c
                                    JOIN payment p ON c.customer_id = p.customer_id
                                    GROUP BY c.customer_id
                                    ORDER BY Total_spent DESC
                                    LIMIT 10;''', con)
print(top10_customers)

plt.figure(figsize=(10,5))
sns.barplot(data=top10_customers, x='name_complete', y='Total_spent')
plt.title('Top 10 Customers by Total Amount Spent')
plt.xlabel('Customer Name')
plt.ylabel('Total Amount Spent')
plt.xticks(rotation=45) 
plt.show()  

#The store in which they buy the customers top 10 is incorporated
top10_customers_store = pd.read_sql(''' SELECT c.first_name || ' ' || c.last_name as name_complete, SUM (p.amount) as Total_spent, c.store_id as Store_ID
                                    FROM customer c
                                    JOIN payment p ON c.customer_id = p.customer_id
                                    GROUP BY c.customer_id
                                    ORDER BY Total_spent DESC
                                    LIMIT 10;''', con)
print(top10_customers_store)

## TOTAL INCOME
film_rental = pd.read_sql(''' SELECT title AS title, SUM(rental_duration) AS rental_duration
                            FROM film
                            GROUP BY title
                            ORDER BY rental_duration DESC;''', con)
print(film_rental)

## Film actor table
actor = pd.read_sql(''' SELECT *
                        FROM film_actor;''', con)
print(actor.head())

## Top 20 actors with most films
top20_actors = pd.read_sql(''' SELECT a.first_name || ' ' || a.last_name AS Actor_Name, COUNT(fa.actor_id) AS quantity_of_films
                            FROM actor a
                            JOIN film_actor fa ON a.actor_id = fa.actor_id
                            GROUP BY a.actor_id, a.first_name, a.last_name
                            ORDER BY quantity_of_films DESC
                            LIMIT 20;''', con)
print(top20_actors) 

plt.figure(figsize=(10,5))
sns.barplot(data=top20_actors, x='Actor_Name', y='quantity_of_films')   
plt.title('Top 20 Actors with Most Films')  
plt.xlabel('Actor Name')    
plt.ylabel('Number of Films')
plt.xticks(rotation=45)
plt.show()

#Payments for Month
payments_per_month = pd.read_sql(''' SELECT strftime('%Y', payment_date) AS year, strftime('%m', payment_date) AS month, SUM(amount) AS total_amount
                                    FROM payment
                                    GROUP BY strftime('%Y', payment_date), strftime('%m', payment_date)
                                    ORDER BY year, month;''', con)    
print(payments_per_month)

payments_per_month['date'] = pd.to_datetime(payments_per_month[['year','month']].assign(day=1))

plt.figure(figsize=(10,5))
plt.scatter(payments_per_month['date'], payments_per_month['total_amount'], color='blue')   
plt.plot(payments_per_month['date'], payments_per_month['total_amount'], color='blue', linestyle='--', label='Total Amount Trend')
plt.xlabel('Date')
plt.ylabel('Total Amount')  
plt.title('Total Payments per Month')
plt.grid(True)
plt.xticks(rotation=45)
plt.tight_layout()

plt.show()

con.close()




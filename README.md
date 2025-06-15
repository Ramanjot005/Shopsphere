
ShopSphere - Deals & Offers Module
==================================

Overview
--------
This Django app is a component of the ShopSphere e-commerce project that manages product deals and discounts. 
It allows admins to create limited-time offers on products, and users to browse active deals with real-time updates.

Features
--------
- Add and manage product deals with title, description, and image
- Apply percentage-based discounts
- Schedule deals with start and end dates
- Automatically show only active deals to users
- Admin dashboard for managing deals
- AJAX-ready endpoints for "Add to Cart" and "Add to Wishlist"

Project Structure
-----------------
- `models.py` : Defines the `Deal` model linked to products
- `views.py`  : Displays active deals and handles business logic
- `urls.py`   : Routes for viewing deals and interacting with the cart/wishlist
- `templates/dealsandoffers/deals_list.html` : Template for listing current deals

Setup Instructions
------------------
1. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```
2. Apply migrations:
   ```bash
   python manage.py migrate
   ```
3. Create a superuser to access the admin panel:
   ```bash
   python manage.py createsuperuser
   ```
4. Run the server:
   ```bash
   python manage.py runserver
   ```
5. Visit `http://localhost:8000/` to view the site.

Folder Notes
------------
- `media/`: Where uploaded deal images are stored
- `db.sqlite3`: Local development database (not for production)

To-Do / Suggestions
-------------------
- Add countdown timer for deal expiration using JavaScript
- Add Deal Detail view for individual offers
- Implement user interaction tracking (clicks, views)
- Build REST API for mobile/frontend apps
- Add full-text search and filtering for deals

License
-------
This project is open-source and free to use.

Author
------
Ramanjot Kaur

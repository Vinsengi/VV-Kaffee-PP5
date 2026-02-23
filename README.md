
## Quick Links

- [Live Application](https://vv-kaffee-5b7b3eb05052.herokuapp.com/)
- [GitHub Repository](https://github.com/Vinsengi/VV-Kaffee)
- [Testing summary](TESTING.md)
- [Validation.md](VALIDATION.md)
![Am I responsive Images](./static/images/readme_images/amiresponsive.png)

---

# VV-Kaffee E-Commerce Website
# 🛒 VV-Kaffee Online Shop

Welcome to **VV-Kaffee E-Commerce Website**! A full-featured online store for VV-Kaffee, offering a seamless shopping experience for Rwandan coffee, products, and more:

- 🛍️ Browse our curated selection of Rwandan coffee and specialty products with easy pagination
- 🛒 Add items to your cart and place orders online
- 📧 Receive email confirmation when your order is successful
- ❌ Cancel your order with a single click

Built with Django, VV-Kaffee makes shopping simple and enjoyable.

---

## Project Overview

VV-Kaffee is an e-commerce web application built with Django, dedicated to selling ethically sourced Rwandan coffee beans to customers in Germany. The project celebrates forgiveness, reconciliation, and Rwanda’s healing journey, with every product telling a story of hope and shared humanity.

---

## 🌍 Story & Mission

This is not just coffee.  
It grows from a land once scarred by division, now healed by forgiveness and reconciliation.  
It is cultivated by healing hearts, and every sip is an invitation to join the journey of reconciliation.

**“Versöhnung und Vergebung Kaffee”** is more than a product — it is a story of hope, healing, and shared humanity.

---

## 🎯 Purpose

This app is designed to help small and medium-sized businesses:
- Accept and manage online orders for VV-Kaffee products
- Display an interactive, image-rich product catalog
- Automate stock checks to prevent overselling
- Store and serve product images reliably through Cloudinary
- Manage order cancellations
- Stay in touch with customers through feedback and contact forms
- Showcase customer reviews
- Allow users to order products for delivery

---
## E-Commerce Business Model

VV-Kaffee follows a **direct-to-consumer (D2C) online retail model**:

- **Value Proposition**
  - Fresh, ethically sourced Rwandan specialty coffee roasted for customers in Germany.
  - Every purchase supports reconciliation and community development in Rwanda.

- **Customer Segments**
  - Coffee enthusiasts in Germany who care about origin and story.
  - Ethical consumers who want their purchases to have social impact.
  - Gift buyers looking for meaningful, story-based products.

- **Revenue Streams**
  - Online sales of coffee beans (250g and 1kg packs).
  - Occasional limited editions and bundles.

- **Channels**
  - VV-Kaffee web shop (this project).
  - Social media (Facebook page, Instagram) to drive traffic to the shop.
  - Newsletter for repeat engagement.

- **Key Activities**
  - Sourcing and roasting coffee.
  - Managing stock and online orders.
  - Packing and shipping orders to customers.
  - Storytelling and community updates via newsletter and social media.

- **Order Lifecycle**
  1. User browses the shop and adds products to the cart.
  2. User checks out using Stripe (card payments).
  3. An order record is created and marked as “paid” after Stripe confirmation.
  4. Fulfilment workflow: the team prepares, packs and dispatches coffee.
  5. Customer receives an email confirmation and can later re-order from their profile.

---

## 🚀 Features

- 👤 **User Accounts & Profiles**  
    - Login via **email or username**  
    - Profile management (address, phone, profile image)  
- Fulfillment team dashboard (via group permissions)  
        ![My Account](./static/images/readme_images/myaccount_fullfillment.png)
- Profile image upload and display for user accounts  
        ![Profile Image Upload Screenshot](./static/images/readme_images/morkup-phone.png)
- Account avatar shown in navigation and profile pages  
        ![Account Avatar Screenshot](./static/images/readme_images/logedin_user_menu2.png)
- 🛒 **Shop & Products**  
    - Categories, coffee details (origin, farm, variety, tasting notes)  
    - Stock tracking & grind selection  
    - Product list with pagination
- 🛍️ **Cart & Checkout**  

    - Session-based shopping cart  
    - Quantity, grind, weight options  
    - Stripe checkout (PaymentIntent)  
    - Email confirmations (pending + paid)
- 📦 **Order Management**  
    - Customers: view orders, re-buy  
    - Staff: fulfillment panel (paid → fulfilled)  
    - Picklist PDF download  
- ⭐ **Reviews**  
    - Customers can leave reviews after order is paid  
- 📧 **Email**  
    - SMTP setup for Gmail or custom SMTP  
    - Order confirmation, status updates
- 📰 **Newsletter Subscription**  
        - Users can subscribe to the VV-Kaffee newsletter for updates, offers, and news  
        - Admins can manage subscribers and send bulk emails  
        - Double opt-in confirmation for GDPR compliance  
        - Unsubscribe link included in every newsletter

## Staff & Fulfillment Modes

- **Concept**: Workers (staff or fulfillment-capable users) have two modes: Work mode (default) and Customer mode (manual toggle). Fulfillment-only users remain non-staff and cannot access Django admin.
- **Navigation & Visibility**: In Work mode, customer links/cart are hidden; only permitted tools appear. Staff see Products/Orders links based on their `products.*` and `orders.*` permissions. Fulfillers see the Fulfillment link if they have `orders.view_fulfillment` or are in the “Fulfillment Department” group. In Customer mode, staff/fulfillment links disappear and standard shop/cart/account links return. A badge plus a full-width toggle button live in the user dropdown.
- **Redirects & Guardrails**: Workers in Work mode who hit customer account/order pages are redirected to the fulfillment queue with an info message. The fulfillment button/card on the account page renders only when the user is in Work mode and has fulfillment access.
- **Permissions & Groups**: Fulfillers need `orders.view_fulfillment` (and typically `orders.change_fulfillment_status`) or membership in “Fulfillment Department.” Product/order managers need the relevant `products.*`/`orders.*` perms. Admin staff set `is_staff=True`; fulfillment-only users can stay non-staff.
- **Mode Behavior Summary**: Workers default to Work mode after login; non-workers stay customer-only. The dropdown toggle switches between Work mode and Customer mode; Customer mode re-enables cart/account for shopping. If links don’t appear, verify permissions/groups and that the user is in Work mode.

---

## 📦 Other Features

- ✅ Public order form with live stock availability
- ✅ Automatic stock management based on orders
- ✅ Product catalog with image upload and Cloudinary integration
- ✅ Get feedback from customers / public
- ✅ Prevents duplicate orders for out-of-stock products
- ✅ Stores customer details with duplicate-check logic
- 📱 **Responsive UI improvements**: Improved mobile layout and form usability
- 💬 **Customer feedback form improvements**: Include numbers rating and comment moderation
- 📊 **Sales analytics dashboard**: Admins can view sales statistics and order trends
- 🔔 **Admin email notifications for every feedback**
- 🗂️ **Order export**: Download order data as CSV for reporting
- 🛡️ **GDPR compliance tools**: Data deletion and privacy controls for users
- 🏷️ **Discount codes**: Support for promotional codes and coupons
- 🧾 **Invoice PDF generation**: Customers can download invoices for their orders
- 🔐 **Advanced Admin Permissions**: Enable role-based access for fulfillment, support, and product management

## 🛠️ Django Admin (Customized)

VV-Kaffee uses a **customized Django admin interface** for efficient management of products, orders, users, and reviews. The admin dashboard features:

- Custom product image previews
- Inline order and review management
- Enhanced filtering and search for products and orders
- Role-based access for fulfillment and support teams

Below is a screenshot of the customized Django admin panel in this project:

![Customized Django Admin vv-kaffee](./static/images/readme_images/admin_login_page.png)

![Customized Django Admin vv-kaffee](./static/images/readme_images/admin_product_page.png)

etc.,....

This interface streamlines admin tasks and provides a clear overview of shop activity, making management simple and intuitive.

---

## 🛠️ Technologies Used

- **Backend:** Django 5.2, Python 3.12  
- **Frontend:** Bootstrap 5 (with custom styling)  
- **Database:** SQLite (dev), PostgreSQL (production via Heroku)  
- **Payments:** Stripe (PaymentIntent + Webhooks)  
- **Authentication:** Django Allauth (Email/Username login)  
- **Media:** Cloudinary (for product images)  
- **PDF:** ReportLab (picklists, receipts)  
- **Deployment:** Heroku (with WhiteNoise static files)  
- HTML/CSS/JavaScript (Bootstrap)
- [python-decouple](https://github.com/HBNetwork/python-decouple)
- [whitenoise](http://whitenoise.evans.io/en/stable/) for static file handling

---


**Rwandan coffee, roasted for Germany.**  
An e-commerce web application built with Django that celebrates forgiveness, reconciliation, and the healing journey of Rwanda.  
This project sells ethically sourced coffee beans from Rwanda, delivering them fresh to customers in Germany.

---

##  🏢 Project Structure

### Data Schema
#### 🗺️ER Diagram (ERD)

![ER Diagram](docs/erd.png)
![ER Diagram](docs/erd2.png)

### 📂 File Structure
```bash
vv-kaffee/
│
├── cart/ # Cart logic & templates
├── orders/ # Checkout, Stripe, fulfillment, picklist PDFs
├── products/ # Product & Category models, shop views
├── profiles/ # User profiles & dashboard
├── reviews/ # Product reviews
│
├── static/ # CSS, JS, branding assets
├── templates/ # Base templates & shared layouts
│ ├── account/ # Allauth login/signup overrides
│ ├── cart/
│ ├── orders/
│ ├── products/
│ ├── profiles/
│ └── reviews/
│
├── versohnung_und_vergebung_kaffee/
│ ├── settings.py
│ ├── urls.py
│ ├── wsgi.py
│ └── asgi.py
│
├── manage.py
└── README.md
```

---

## 🏠 Home Page Wireframe

Below is a wireframe image representing the layout of the VV-Kaffee home page:

![Home Page Wireframe](./static/images/readme_images/home-wireframe.jpg)

This wireframe illustrates the main sections: logo, cart, hero message, call-to-action button, and footer.

## 🛒 Shop Page Wireframe

Below is a wireframe image representing the layout of the VV-Kaffee shop/products page:

![Shop Page Wireframe](./static/images/readme_images/product_wireframe.jpg)

This wireframe illustrates the main sections: product grid (cards with image, price, and view button), pagination controls, and a clean, responsive layout for browsing products.

## 📋 Recent Orders Wireframe

Below is a wireframe image representing the layout of the VV-Kaffee "Recent Orders" page:

![Recent Orders Wireframe](./static/images/readme_images/my_account_wireframe.png)

This wireframe shows a table listing recent orders, including columns for order number, date, status, total amount, and quick actions (view, cancel, reorder). The design ensures users can easily track and manage their recent purchases.

## 🛒 Cart Page Wireframe

Below is a wireframe image representing the layout of the VV-Kaffee cart page:

![Cart Page Wireframe](./static/images/readme_images/cart-function.png)

This wireframe shows the main cart table with columns for item, grind, quantity, unit, line total, and a remove button. Below the table, subtotal, shipping, and total amounts are displayed, along with a prominent checkout button for a clear and user-friendly shopping experience.

---

## 📦 Setup Instructions (Local Development)

### 1. Clone the repository

```bash
git clone https://github.com/your-username/vv-kaffee-ecommerce.git
cd vv-kaffee-ecommerce
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Setup Environment Variables

Create a `.env` file in the root directory:

```dotenv
SECRET_KEY=your_django_secret_key
DEBUG=True

# Email settings
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
DEFAULT_FROM_EMAIL=your_email@gmail.com
# Site metadata for emails/links
SITE_URL=http://127.0.0.1:8000
SITE_NAME=VV Kaffee
# Send internal alerts to these addresses when orders are paid (comma-separated)
ORDER_NOTIFICATION_EMAILS=ops@example.com,team@example.com

# PostgreSQL (used by Heroku)
DATABASE_URL=postgres://user:password@host:port/dbname
```

### 5. Apply Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create a Superuser

```bash
python manage.py createsuperuser
```

### 7. Run the Development Server

```bash
python manage.py runserver
```

- Internal UI sandbox: while logged in, visit `/testbed/` to preview components in `templates/test_base.html` without affecting live pages.

---

## 🌍 Deploying to Heroku

### 1. Prerequisites

- Install [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)
- Run `heroku login`
- Create a Heroku account

### 2. Setup Heroku

```bash
heroku create your-app-name
```

### 3. Add Heroku PostgreSQL

```bash
heroku addons:create heroku-postgresql:hobby-dev
```

### 4. Set Environment Variables on Heroku

```bash
heroku config:set SECRET_KEY=your_django_secret_key
heroku config:set DEBUG=False
heroku config:set ALLOWED_HOSTS=your-app-name.herokuapp.com

# Email variables
heroku config:set EMAIL_HOST=smtp.gmail.com
heroku config:set EMAIL_PORT=587
heroku config:set EMAIL_USE_TLS=True
heroku config:set EMAIL_HOST_USER=your_email@gmail.com
heroku config:set EMAIL_HOST_PASSWORD=your_app_password
heroku config:set DEFAULT_FROM_EMAIL=your_email@gmail.com
```

### 5. Prepare for Heroku

Ensure these files exist:

- `Procfile`

```makefile
web: gunicorn vv_kaffee.wsgi
```

- `requirements.txt`

```bash
pip freeze > requirements.txt
```

python-3.12.6
```

### 6. Deploy

```bash
git add .
git commit -m "Ready for Heroku deployment"
git push heroku main
```

Alternatively, you can deploy manually using the Heroku web UI:

1. Go to [Heroku Dashboard](https://dashboard.heroku.com/) and log in.
2. Click "New" > "Create new app" and enter your app name.
3. Select your region and click "Create app".
4. In the "Deploy" tab, choose "GitHub" as the deployment method.
5. Connect your GitHub repository and select the branch to deploy.
6. Click "Deploy Branch" to start deployment.
7. After deployment, go to the "Resources" tab and add the Heroku PostgreSQL add-on.
8. Set your environment variables in the "Settings" tab under "Config Vars".
9. Run migrations using the "Run Console" feature in the "More" dropdown.
10. Visit your app URL to verify the deployment.

### 7. Run Migrations on Heroku

```bash
heroku run python manage.py migrate
heroku run python manage.py createsuperuser
```

---

## 📸 Featured Products

The app highlights products such as:

- Rwandan Coffee Beans ☕
- Versöhnung & Vergebungskaffee
- Question Coffee
- Kivu Bourbon 250g
- Kivu Bourbon 1kg
- Nyungwe Natural 250g
- Muhazi Espresso 500g

Each is displayed with consistent image styling and pagination for better UX.

---

## 📧 Email Notifications

The system is configured to send:
- Order emails (pending + paid) using your SMTP credentials.
- New user signup flow: Allauth sends a confirmation email and the app sends a welcome email after registration.

Emails include links so users can go to their account and manage their orders, profile, etc.

---

## ✅ Manual Testing

| Feature                | Steps                                                                                   |
|------------------------|-----------------------------------------------------------------------------------------|
| Order Placement        | Go to `/cart/`, add products, and complete checkout. Confirm order appears in admin/DB. |
| Duplicate Prevention   | Attempt to order an out-of-stock item; system should prevent duplicate orders.          |
| Cancel Order           | Access `/cancel/`, submit cancellation, and verify order is removed from records.       |
| Product Image Display  | Add a product with an image; check that it displays correctly on `/products/`.          |
| Cart Functionality     | Add, update, and remove items in the cart; verify totals and quantities update.         |
| Email Confirmation     | Place an order and confirm receipt of a confirmation email.                             |
| User Signup Emails     | Register a new account and verify both the confirmation email and the welcome email arrive. |
| Review Submission      | After order completion, submit a product review and check it appears on the site.       |
| Newsletter Signup      | Subscribe to the newsletter and verify confirmation and double opt-in email.            |
| Admin Dashboard        | Log in as admin, view orders, manage products, and export order data as CSV.            |
| Responsive Design      | Test site layout and usability on mobile, tablet, and desktop devices.                  |

---

## 🧪 Test Results

Below are screenshots showing successful test runs for the VV-Kaffee project:

### ✅ Example: Accessibility Testing Results
Accessibility checks were performed using [Lighthouse](https://developer.chrome.com/docs/lighthouse/accessibility/), and [WAVE](https://wave.webaim.org/):

![Accessibility Test Results](./static/images/readme_images/home-wave-test.png)

### ✅ Example: Shop Page Accessibility Test

Accessibility testing was performed on the shop/products page using [Lighthouse](https://developer.chrome.com/docs/lighthouse/accessibility/) and [WAVE](https://wave.webaim.org/):

![Shop Page Accessibility Test](./static/images/readme_images/shop_page_wave_test.png)

This screenshot demonstrates that the shop page meets accessibility standards, with clear navigation, readable text, and proper labeling for assistive technologies.

### ✅ Example: Cart Page Accessibility Test

Accessibility testing was performed on the cart page using [WAVE](https://wave.webaim.org/):

![Cart Page Accessibility Test](./static/images/readme_images/cart-wave-test.png)

This screenshot demonstrates that the cart page meets accessibility standards, with clear table structure, readable labels, and keyboard navigation support.

### ✅ Example: Checkout Page Accessibility Test

Accessibility testing was performed on the checkout page using [Lighthouse](https://developer.chrome.com/docs/lighthouse/accessibility/) and [WAVE](https://wave.webaim.org/):

![Checkout Page Accessibility Test](./static/images/readme_images/check-out-wave-test.png)

This screenshot demonstrates that the checkout page meets accessibility standards, with clear form fields, proper labels, and keyboard navigation support.

> The above screenshots show just a few examples of the many manual and accessibility tests performed during development. Comprehensive testing was carried out across all major features and pages to ensure reliability, usability, and accessibility for all users.

---

## 🧪 Automated Testing

Run all tests with:

```bash
python manage.py test
```

Example test:

```python
from django.test import TestCase
from .models import Order

class OrderTestCase(TestCase):
        def test_order_creation(self):
                order = Order.objects.create(name='John', email='john@example.com', ...)
                self.assertEqual(Order.objects.count(), 1)
```

Use `unittest.mock` or `pytest-django` to simulate image uploads if needed.

### 🧹 Linting

Install the project linters (development dependency):

```bash
python -m pip install flake8
```

Run style checks across the Django apps:

```bash
flake8 cart newsletter orders products profiles reviews versohnung_und_vergebung_kaffee
```

Lint configuration lives in `.flake8` at the project root. Migrations and virtual environments are excluded from checks.

---

## 🧰 Deployment Notes

To deploy this project:
- Ensure all Cloudinary credentials are added to the environment.
- Use Heroku or any cloud service with Django + PostgreSQL support.
- Set `DEBUG = False` and configure `ALLOWED_HOSTS` in production.

---

## 🙋 Contributing

Contributions are welcome! Please fork the repository, create a new branch, and open a pull request with your improvements or fixes.

---

## 🚀 Features Planned for the Next Release

- 📨 **Order Cancellation Emails**: Automatically notify customers via email when their order is cancelled
- 🌐 **Multilingual Support**: Add English and French language options for the storefront and emails
- 🗓️ **Admin Calendar View**: Visualize daily orders and fulfillment tasks in a calendar interface
- ⚙️ **Preferred Product Selection**: Allow returning customers to save and quickly reorder favorite products
- 📅 **Store Opening Hours**: Display shop operating hours and holiday closures on the website
- 🗺️ **Interactive Map**: Show coffee origins and shop location with map integration
- 💳💶 **Enhanced Online Payments**: Expand payment options and improve checkout flow (E.g: Paypal)
- 🥘 **Updated Branding**: Refine VV-Kaffee logo and visual identity across the site

Watch the [GitHub repository](https://github.com/your-username/vv-kaffee-ecommerce) for updates and milestone progress.

---

## 🐞 Known Bugs

The following issues are currently being tracked:

- ⚠️ **Admin panel product image preview**: Uploaded images may not display immediately in the admin panel; a manual refresh is sometimes needed.
- 🕐 **Order stock conflicts**: Double orders can occur if two users submit purchases at the same time, due to race conditions.
- 📧 **Cancellation email not sent**: Users do not receive an email confirmation when cancelling an order; this feature is pending implementation.
- 📆 **Date/time picker inconsistencies**: Some mobile browsers display date/time input fields incorrectly.
- 📱 **Product layout on small screens**: Product images and items may overlap or stack awkwardly on very narrow devices.

All bugs are logged for future fixes. Please report new issues or contribute solutions via GitHub Issues.

---

## 🧩 Agile Development Approach

VV-Kaffee is built using Agile principles for rapid, flexible delivery. The team works in sprints, releasing new features and improvements iteratively. A prioritized backlog tracks tasks, bugs, and enhancements. User stories guide development to meet real customer and admin needs. Manual and automated testing after each sprint ensures quality and fast feedback. The roadmap adapts based on user input and test results, keeping the project focused on business value and usability.

---

## 🖼️ Example Project Image: Knabahn

Below is an example image representing the Knabahn project:

![Knabahn Project Screenshot](./static/images/readme_images/agile-methodology-development.png)
![Knabahn Project Screenshot](./static/images/readme_images/left_to_do.png)

Project images are displayed with consistent styling and a responsive layout across all devices.

---

## 🖥️ For Non-Developers: How This Was Built

This website was created using **Django** (a tool developers use to build websites). It connects to a database that stores all our products and order details.

- Your orders are saved securely
- Product pictures are added by the admin team
- Emails are sent automatically when you order

---

## 🚀 How We Shared This Site with the World (Deployment)

We used **Heroku**, a hosting service, to put the website online. Think of it like putting VV-Kaffee on Google Maps – now everyone can find and use it!

Steps involved:
1. We signed up on Heroku
2. Connected our website to Heroku
3. Set up the database and email settings there
4. Published it online

---

## 🗂️ About the Products Page

On the **products page**, you’ll find:
- Paginated list (like flipping pages of a photo album)
- Product names and pictures
- “Add to cart” buttons, so you can order your favorite easily
- Option to view details for every product, including origin, tasting notes, and more

---
## 🙂📖 Facebook Page

For marketing strategy purposes, a facebook page has been added to reach out to our potential customers who use facebook. the page will keep improving.
![Facebook Page Screenshot](./static/images/readme_images/fbk_page.png)
![Facebook Page Screenshot](./static/images/readme_images/fcbk_page2.png)
![Facebook Page Screenshot](./static/images/readme_images/fcbk_page3.png)
![Facebook Page Screenshot](./static/images/readme_images/fcbk_page4.png)
![Facebook Page Screenshot](./static/images/readme_images/fcbk_page5.png)

---

## 📧 About Email Confirmation

When you order:
- An email is sent automatically to confirm your purchase
- It includes your name, order time, and selected products

---

## 🌍 Want to Help or Share Ideas?

You can reach out to the admin team with suggestions, product ideas, or feedback. We’d love to improve the experience!

Thank you for visiting VV-Kaffee – enjoy your shopping! 🇷🇼☕

---

## 🧰 Complete Local Setup Guide

### 1. Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Setup Environment Variables

Create a `.env` file in the root directory:

```dotenv
SECRET_KEY=your_django_secret_key
DEBUG=True

# Email settings
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
DEFAULT_FROM_EMAIL=your_email@gmail.com
# Site metadata for emails/links
SITE_URL=http://127.0.0.1:8000
SITE_NAME=VV Kaffee

# PostgreSQL (used by Heroku)
DATABASE_URL=postgres://user:password@host:port/dbname
```

### 4. Apply Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create a Superuser

```bash
python manage.py createsuperuser
```

### 6. Run the Development Server

```bash
python manage.py runserver
```

---

## 🗂 Project Structure in Brief

```bash
VV-Kaffee/
├── cart/                # Cart management (templates, views, models)
├── newsletter/          # Newsletter subscription
├── orders/              # Order processing and history
├── products/            # Product catalog and details
├── profiles/            # User profile management
├── reviews/             # Product reviews
├── static/              # Static files (CSS, images, JS)
├── staticfiles/         # Collected static files for deployment
├── templates/           # Shared templates (base.html, home.html, etc.)
├── vv_kaffee/           # Main Django project settings
├── manage.py            # Django management script
```

---

## ✅ Future Enhancements

- Enhanced admin dashboard and analytics
- Improved mobile and accessibility features
- Expanded payment options (e.g., PayPal)
- Order cancellation email notifications
- Interactive map for coffee origins
- Calendar view for admin order management
- Preferred product selection for returning customers
- Store opening hours display
- Updated branding and visual identity
- Multilingual support

## 🤝 Credit and Acknowledgments

- Inspired by traditional Rwandan coffee and culture
- Thanks to the AI
- Thanks to Code Institute student support Team and Student care Team for their support

